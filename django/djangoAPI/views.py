import csv
import os
import json
import random
import requests
from datetime import date, timedelta

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from django.db import transaction, connection
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from djangoAPI.models import *
from djangoAPI.utils import num_to_alpha


def init_db2():
    '''
    Initilize the DB with extensions, views and ltree specific triggers
    '''
    with connection.cursor() as cursor:
        try:
            cursor.execute('CREATE EXTENSION ltree;')
        except Exception as e:
            print(type(str(e)))
            print(str(e))
        try:
            cursor.execute('''
            ALTER TABLE public."djangoAPI_ProjectAssetRoleRecordTbl" DROP COLUMN ltree_path;
            ALTER TABLE public."djangoAPI_ProjectAssetRoleRecordTbl" ADD COLUMN ltree_path ltree;
            CREATE INDEX parent_id_idx ON public."djangoAPI_ProjectAssetRoleRecordTbl" USING GIST (ltree_path);
            CREATE INDEX parent_path_idx ON public."djangoAPI_ProjectAssetRoleRecordTbl" (parent_id_id);
            ALTER TABLE public."djangoAPI_AvantisAdditions" DROP COLUMN full_path;
            ALTER TABLE public."djangoAPI_AvantisAdditions" ADD COLUMN full_path ltree;
            CREATE INDEX aa_parent_id_idx ON public."djangoAPI_AvantisAdditions" USING GIST (full_path);
            CREATE INDEX aa_parent_path_idx ON public."djangoAPI_AvantisAdditions" (parent_mtoi_id);
            ''')
        except Exception as e:
            print(type(str(e)))
            print(str(e))
        try:
            cursor.execute('''
        CREATE OR REPLACE FUNCTION update_parent_path() RETURNS TRIGGER AS $$
            DECLARE
                path ltree;
            BEGIN
                IF NEW.parent_id_id IS NULL THEN
                    NEW.ltree_path = ((new.id::text)::ltree);
                ELSEIF TG_OP = 'INSERT' OR OLD.parent_id_id IS NULL OR OLD.parent_id_id != NEW.parent_id_id THEN
                    SELECT ltree_path FROM public."djangoAPI_ProjectAssetRoleRecordTbl" WHERE id = NEW.parent_id_id INTO path;
                    IF path IS NULL THEN
                        RAISE EXCEPTION 'Invalid parent_id %. Entities must be added parents first', NEW.parent_id_id;
                    END IF;
                    path = path || new.id::text;
                    NEW.ltree_path = path;
                    UPDATE public."djangoAPI_ProjectAssetRoleRecordTbl"
                        SET ltree_path = path || subpath(ltree_path,nlevel(OLD.ltree_path)) WHERE ltree_path <@ OLD.ltree_path and ltree_path != old.ltree_path;
                END IF;
                RETURN NEW;
            END;
        $$ LANGUAGE plpgsql;
        ''')
        except Exception as e:
            print(type(str(e)))
            print(str(e))
        try:
            cursor.execute(
                '''
        CREATE TRIGGER parent_path_tgr
            BEFORE INSERT OR UPDATE ON public."djangoAPI_ProjectAssetRoleRecordTbl"
            FOR EACH ROW EXECUTE PROCEDURE update_parent_path();
        ''')
        except Exception as e:
            print(type(str(e)))
            print(str(e))
        try:
            cursor.execute('''
        CREATE OR REPLACE FUNCTION update_avantis_additions() RETURNS TRIGGER AS $$
            DECLARE
                ltree_path ltree;
                old_path ltree;
                parent_mtoi int;
            BEGIN
                select mtoi from public."djangoAPI_ClonedAssetAndRoleInRegistryTbl" where role_number = new.parent_role_number into parent_mtoi;
                IF NEW.parent_role_number = '' then
                    raise notice 'parent role number is empty';
                    ltree_path = ((new.mtoi::text)::ltree);
                else
                    raise notice 'parent role number is NOT empty';
                    SELECT full_path FROM public."djangoAPI_AvantisAdditions" WHERE clonedassetandroleinregistrytbl_ptr_id = parent_mtoi INTO ltree_path;
                    IF ltree_path IS NULL THEN
                        RAISE EXCEPTION 'Invalid parent_id %. Entities must be added parents first', NEW.parent_role_number;
                    END IF;
                    ltree_path = ltree_path || new.mtoi::text;
                    raise notice 'ltree_path is %', ltree_path;
                end if;
                if TG_OP = 'INSERT' then
                    insert into public."djangoAPI_AvantisAdditions"(clonedassetandroleinregistrytbl_ptr_id, full_path, parent_mtoi_id) values(new.mtoi, ltree_path, parent_mtoi);
                elseif TG_OP = 'UPDATE' then 
                    raise notice 'updating old values';
                    select full_path from public."djangoAPI_AvantisAdditions" where clonedassetandroleinregistrytbl_ptr_id = new.mtoi into old_path;
                    update public."djangoAPI_AvantisAdditions" set full_path = ltree_path, parent_mtoi_id = parent_mtoi where clonedassetandroleinregistrytbl_ptr_id = new.mtoi;
                    UPDATE public."djangoAPI_AvantisAdditions"
                        SET full_path = ltree_path || subpath(full_path,nlevel(old_path)) WHERE full_path <@ old_path and full_path != old_path;
                end if;
                RETURN NEW;
            END;
        $$ LANGUAGE plpgsql;
        ''')
        except Exception as e:
            print(type(str(e)))
            print(str(e))
        try:
            cursor.execute('''
        CREATE TRIGGER avantis_additions_tgr
            BEFORE INSERT OR UPDATE ON public."djangoAPI_ClonedAssetAndRoleInRegistryTbl"
            FOR EACH ROW EXECUTE PROCEDURE update_avantis_additions();
        ''')
        except Exception as e:
            print(type(str(e)))
            print(str(e))

        cursor.execute('''
        create or replace
        view reconciliation_view_temp as
        select
            r.id,
            r.updatable_role_number as role_number,
            r.role_name as role_name,
            r.parent_id_id as parent,
            r.project_tbl_id as project_id,
            r.entity_exists as role_exists,
            r.missing_from_registry as role_missing_from_registry,
            r.ltree_path as full_path,
            r.parent_changed as parent_changed,
            a.id as asset_id,
            a.asset_serial_number as asset_serial_number,
            coalesce(a.entity_exists, false) as asset_exists,
            coalesce(a.missing_from_registry, false) as asset_missing_from_registry,
            coalesce(a.role_changed, false) as role_changed,
            r.approved as approved
        from
            ( public."djangoAPI_ProjectAssetRoleRecordTbl" as br
        right join public."djangoAPI_PreDesignReconciledRoleRecordTbl" as pr on
            (br.id = pr.projectassetrolerecordtbl_ptr_id)) as r
        left join ( public."djangoAPI_PreDesignReconciledAssetRecordTbl" as pa
        left join public."djangoAPI_ProjectAssetRecordTbl" as ba on
            (pa.projectassetrecordtbl_ptr_id = ba.id)) as a on
            (r.id = a.initial_project_asset_role_id_id);
        ''')
        cursor.execute('''
        create or replace
        view reconciliation_view as
        select
            r.id,
            r.role_number,
            r.role_name,
            r.parent,
            r.project_id,
            r.role_exists,
            r.role_missing_from_registry,
            subpath(r.full_path, 1) as full_path,
            r.parent_changed,
            r.asset_id,
            r.asset_serial_number,
            r.asset_exists,
            r.asset_missing_from_registry,
            r.role_changed,
            r.approved
        from
            reconciliation_view_temp as r
        where
            r.full_path <@ '1'::ltree;
        ''')
        cursor.execute('''
        create or replace
        view orphan_view as
        select
            r.id,
            r.role_number,
            r.role_name,
            r.parent,
            r.project_id,
            r.role_exists,
            r.role_missing_from_registry,
            subpath(r.full_path, 1) as full_path,
            r.parent_changed,
            r.asset_id,
            r.asset_serial_number,
            r.asset_exists,
            r.asset_missing_from_registry,
            r.role_changed
        from
            reconciliation_view_temp as r
        where
            r.full_path <@ '2'::ltree;
        ''')
        cursor.execute('''
        create or replace
        view unassigned_assets as
        select
            ba.id as id,
            ba.asset_serial_number as asset_serial_number,
            pa.missing_from_registry as asset_missing_from_registry,
            ba.project_tbl_id
        from
            public."djangoAPI_PreDesignReconciledAssetRecordTbl" as pa
        left join public."djangoAPI_ProjectAssetRecordTbl" as ba on
            pa.projectassetrecordtbl_ptr_id = ba.id
        where
            pa.initial_project_asset_role_id_id is null
            and pa.designer_planned_action_type_tbl_id <> 'b';
        ''')
        cursor.execute('''
        create or replace
        view reservation_view as
        select
            mtoi as id,
            role_number,
            role_name,
            parent_mtoi_id as parent,
            project_tbl_id as project_id,
            full_path,
            approved,
            (not project_tbl_id is null) as reserved,
            (case
                when (approved) and (not project_tbl_id is null) then 'Approved'
                -- true + true
                when (not approved) and (not project_tbl_id is null) then 'Pending'
                -- false + true
            end ) as approval_status,
            (role_exists and asset_exists and (not parent_changed) and (not role_changed)) as reservable
        from
            ((public."djangoAPI_ClonedAssetAndRoleInRegistryTbl" as c
        left join public."djangoAPI_AvantisAdditions" as a on
            c.mtoi = a.clonedassetandroleinregistrytbl_ptr_id) as ca
        left join ((select projectassetrolerecordtbl_ptr_id, entity_exists as role_exists, parent_changed, cloned_role_registry_tbl_id from public."djangoAPI_PreDesignReconciledRoleRecordTbl") as pa
        left join (select id, approved, project_tbl_id from public."djangoAPI_ProjectAssetRoleRecordTbl") as ra on
            pa.projectassetrolerecordtbl_ptr_id = ra.id) as pr on
            ca.mtoi = pr.cloned_role_registry_tbl_id) as d
        left join (select projectassetrecordtbl_ptr_id, entity_exists as asset_exists, role_changed, cloned_role_registry_tbl_id from public."djangoAPI_PreDesignReconciledAssetRecordTbl") as e on
            d.mtoi = e.cloned_role_registry_tbl_id;
        ''')
        try:
            cursor.execute('''
            CREATE OR REPLACE FUNCTION update_parent_changed() RETURNS TRIGGER AS $$
            -- only run on updates, since insert implies that the entity did not exist in avantis to begin with, which means this does not apply (false)
                DECLARE
                new_parent_mtoi int;
                orig_parent_mtoi int;
                status bool;
                begin
            --	    only run trigger if the entry is predesign
                    if exists (select 1 from public."djangoAPI_PreDesignReconciledRoleRecordTbl" as rr1 where rr1.projectassetrolerecordtbl_ptr_id = new.id) then
                        status = false;
                        IF OLD.parent_id_id != NEW.parent_id_id then
                            select
                                cloned_role_registry_tbl_id
                            from
                                public."djangoAPI_PreDesignReconciledRoleRecordTbl"
                            where
                                projectassetrolerecordtbl_ptr_id  = new.parent_id_id
                            into
                                new_parent_mtoi;
                            
                            select
                                mtoi
                            from
                                public."djangoAPI_ClonedAssetAndRoleInRegistryTbl"
                            where
                                role_number = (
                                select
                                    parent_role_number
                                from
                                    public."djangoAPI_ClonedAssetAndRoleInRegistryTbl"
                                where
                                    mtoi = (
                                    select
                                        cloned_role_registry_tbl_id
                                    from
                                        public."djangoAPI_PreDesignReconciledRoleRecordTbl"
                                    where
                                        projectassetrolerecordtbl_ptr_id = new.id))
                            into
                                orig_parent_mtoi;
            --				raise exception 'new mtoi %, old mtoi %', new_parent_mtoi, orig_parent_mtoi;
                            if new_parent_mtoi <> orig_parent_mtoi then
                                status = true;
                            end if;
                        END IF;
                        update public."djangoAPI_PreDesignReconciledRoleRecordTbl" as rr set parent_changed = status where rr.projectassetrolerecordtbl_ptr_id = new.id;
                    end if;
                    RETURN NEW;
                END;
            $$ LANGUAGE plpgsql;
        ''')
        except Exception as e:
            print(type(str(e)))
            print(str(e))
        try:
            cursor.execute(
                '''
        CREATE TRIGGER parent_changed_tgr
            BEFORE insert or UPDATE ON public."djangoAPI_ProjectAssetRoleRecordTbl"
            FOR EACH ROW EXECUTE PROCEDURE update_parent_changed();
        ''')
        except Exception as e:
            print(type(str(e)))
            print(str(e))
        try:
            cursor.execute('''
        CREATE OR REPLACE FUNCTION update_role_changed() RETURNS TRIGGER AS $$
        -- only run on updates, since insert implies that the entity did not exist in avantis to begin with, which means this does not apply (false)
            DECLARE
            new_role_mtoi int;
            orig_role_mtoi int;
            status bool;
            begin
        --	    only run trigger if the entry is predesign
                status = false;
			--	raise exception 'new role %, old role %', NEW.initial_project_asset_role_id_id, OLD.initial_project_asset_role_id_id;
                IF OLD.initial_project_asset_role_id_id != NEW.initial_project_asset_role_id_id or OLD.initial_project_asset_role_id_id is null or NEW.initial_project_asset_role_id_id is null then
                    new_role_mtoi = new.cloned_role_registry_tbl_id;
                    select cloned_role_registry_tbl_id from public."djangoAPI_PreDesignReconciledRoleRecordTbl"  as rr where rr.projectassetrolerecordtbl_ptr_id = new.initial_project_asset_role_id_id into orig_role_mtoi;
           --     	raise exception 'new role %, old role %', new_role_mtoi, orig_role_mtoi;
                if new_role_mtoi <> orig_role_mtoi then
                        status = true;
                    end if;
                END IF;
                new.role_changed = status;
                RETURN NEW;
            END;
        $$ LANGUAGE plpgsql;
        ''')
        except Exception as e:
            print(type(str(e)))
            print(str(e))
        try:
            cursor.execute('''
            create trigger role_changed_tgr
            before insert or update on public."djangoAPI_PreDesignReconciledAssetRecordTbl"
            for each row execute procedure update_role_changed();
        ''')
        except Exception as e:
            print(type(str(e)))
            print(str(e))


def init_db(request):
    init_db2()
    return HttpResponse("Finished DB init")


def db_fill2():
    '''
    Fill the DB with test data
    Will eventually switch to initialization with constants for list tables
    '''
    InitEnums()
    InitValueList()
    for i in range(4):
        DesignProjectTbl.objects.create(
            pk=i+1,
            planned_date_range=(date.today(), date.today() + timedelta(days=40)),
            op_bus_unit_id=['a', 'b', 'c', 'd'][i],
        )
    lst = [['Super', 'User'], ['Tony', 'Huang'], ['Peter', 'Lewis'], ['Stephen', 'Almeida']]
    for i, value in enumerate(lst):
        UserTbl.objects.create(
            id=i+1,
            first_name=value[0],
            last_name=value[1],
            username=value[0]+'.'+value[1],
            organization_name='TW',
            email=value[0]+'.'+value[1]+'@admin.ca',
            user_type_id=1,
        )
    for i in range(3):
        for j in range(3):
            DesignProjectHumanRoleTbl.objects.create(
                user_id_id=j+1,
                design_project_id=i+1,
                human_role_type_id=num_to_alpha(j+1),
            )
    today = date.today()
    for i in range(2):
        today = today + timedelta(days=5)
        for j in range(3):
            DesignStageTbl.objects.create(
                pk=i*3+j,
                planned_date_range=(today-timedelta(days=5), today),
                design_stage_type_id=[
                    'a', 'b', 'c', 'd', 'e'][j],
                design_project_id=j+1,
            )
    today = date.today() + timedelta(days=10)
    for i in range(2):
        today = today + timedelta(days=15)
        for j in range(3):
            ConstructionPhaseTbl.objects.create(
                pk=i*3+j,
                planned_date_range=(today-timedelta(days=15), today),
                phase_number=i,
                design_project_id=j + 1,
                scope_description='a project construction phase',
                op_bus_unit_id=['a', 'b', 'c'][i],
            )
    for i in range(3):
        for j in range(3):
            ConstructionPhaseHumanRoleTbl.objects.create(
                user_id_id=j+1,
                construction_phase_id=i+1,
                human_role_type_id=num_to_alpha(j+1),
            )
    today = date.today() + timedelta(days=10)
    for i in range(2):
        today = today + timedelta(days=5)
        for j in range(3):
            ConstructionStageTbl.objects.create(
                pk=i*3+j,
                planned_date_range=(today-timedelta(days=5), today),
                construction_phase_id=i+1,
                construction_stage_type_id=[
                    'a', 'b', 'c', 'd', 'e'][j],
            )
    asset_line = {}
    with open('avantis.csv', mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            line_count = line_count + 1
            asset_line[row[0]] = [line_count, row]

    # create a location for states
    spatial_state = ImportedSpatialSiteTbl.objects.create(
        name='Virtual Spatial Location for States',
    )
    # if pk is specified the autogeneration will not see the entry and will generate conflicting primary keys
    spatial_state.pk = 1
    spatial_state.save()

    # create spatial sites
    locations = {}
    for asset_row in asset_line.items():
        if not locations.get(asset_row[1][1][7]):
            spatial_site = ImportedSpatialSiteTbl.objects.create(
                name=asset_row[1][1][7]
            )
            locations[asset_row[1][1][7]] = [spatial_site.pk, asset_row[1][1][3], spatial_site]
    for location in locations.values():
        temp = asset_line.get(location[1])
        if temp:
            temp = locations.get(temp[1][7])
            spatial_site = location[2]
            if temp:
                spatial_site.parent_site_id_id = temp[0]
                spatial_site.save()

    for asset_row in asset_line.items():
        avantis_asset = ClonedAssetAndRoleInRegistryTbl.objects.create(
            mtoi=asset_row[1][0],
            role_number=asset_row[0],
            role_name=asset_row[1][1][1],
            parent_role_number=asset_row[1][1][3],
            role_location=asset_row[1][1][7],
            role_criticality=asset_row[1][1][6],
            role_priority=5,  # did not exist in my avantis import
            role_equipment_type='meh',
            role_classification='does this even matter right now?',
            asset_serial_number='dont have this value either',
            suspension_id=1,
            already_reserved_id=1,
            intent_to_reserve_id=1,
            role_spatial_site_id_id=locations[asset_row[1][1][7]][0],
        )

    # create our state roles
    states = ['Top Level Roles', 'Orphaned Roles']
    for i in range(10):
        role = ProjectAssetRoleRecordTbl.objects.create(
            updatable_role_number='State ' + str(i+1),
            role_name=states[i] if i < len(states) else 'Reserved for Future State',
            parent_id_id=None,
            role_criticality_id='a',
            role_priority_id='a',
            role_spatial_site_id_id='1',
            project_tbl_id=1,
        )
        role.pk = i + 1
        role.save()


def db_fill(request):
    db_fill2()
    return HttpResponse("Finished DB Fill")


def update_asset_role2():
    cloned_assets = ClonedAssetAndRoleInRegistryTbl.objects.all()
    parent_mtoi = {}  # dictionary for quickly finding entry by role number
    for entry in cloned_assets:  # populate dict, keys = role number
        if entry.role_number in parent_mtoi.keys():
            pass
        else:
            parent_mtoi[entry.role_number] = entry

    base_role_dict = {}  # dictionary for tracking roles and its pk
    with transaction.atomic():
        for entry in cloned_assets:
            existing_role = PreDesignReconciledRoleRecordTbl.objects.create(
                updatable_role_number=entry.role_number,
                role_name=entry.role_name,
                parent_id_id=None,  # fill this in on the second go
                role_criticality_id=num_to_alpha(entry.role_criticality),
                role_priority_id=num_to_alpha(entry.role_priority),
                role_spatial_site_id=entry.role_spatial_site_id,
                cloned_role_registry_tbl_id=parent_mtoi[entry.role_number].mtoi,
                entity_exists=True,
                missing_from_registry=False,
                designer_planned_action_type_tbl_id=num_to_alpha(3),  # do nothing
                parent_changed=False,
            )
            base_role_dict[existing_role.updatable_role_number] = existing_role.pk
    base_roles = ProjectAssetRoleRecordTbl.objects.all()
    # with transaction.atomic():
    for role in base_roles:
        try:  # update the parent of roles unless its top level in which case it is suppose to be child of 1
            role.parent_id_id = base_role_dict.get(
                parent_mtoi[role.updatable_role_number].parent_role_number, 1)
            role.save()
        except Exception as e:
            print('cant save parent for ' +
                  role.updatable_role_number + str(type(e)) + str(e))
        else:
            print('saved parent for ' + role.updatable_role_number)
    # populate predesign asset records
    with transaction.atomic():
        for entry in cloned_assets:
            existing_asset = PreDesignReconciledAssetRecordTbl()
            existing_asset.asset_serial_number = 'ASN ' + entry.role_number
            existing_asset.cloned_role_registry_tbl_id = parent_mtoi[entry.role_number].mtoi
            existing_asset.initial_project_asset_role_id_id = base_role_dict[entry.role_number]
            existing_asset.entity_exists = True
            existing_asset.missing_from_registry = False
            existing_asset.designer_planned_action_type_tbl_id = num_to_alpha(3)  # do nothing
            existing_asset.role_changed = False
            existing_asset.save()


def update_asset_role(request):
    update_asset_role2()
    return HttpResponse('Finished Updating Asset & Role')


def test(request):
    message = Mail(
        from_email='amber.brasher@toronto.ca',
        to_emails='jon.ma@toronto.ca',
        subject='Meeting with Annette',
        html_content='<strong>Annette is holding me hostage in the Taylor-Massey Creek meetin room</strong>')
    try:
        sg = SendGridAPIClient(
            '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')
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        return HttpResponse(response.headers)
    except Exception as e:
        return HttpResponse('error ' + str(e))


def init_all(request):
    init_db2()
    db_fill2()
    update_asset_role2()
    subdomain = os.getenv('BRANCH', '')
    tables = ['reconciliation_view', 'orphan_view', 'reservation_view', 'unassigned_assets']
    for table in tables:
        response = requests.post(
            'https://hasura.' + subdomain + '.duckdns.org/v1/query',
            json={
                "type": "track_table",
                "args": {
                    "table": {
                        "schema": "public",
                        "name": table
                    }
                }
            },
            headers={'x-hasura-admin-secret': 'eDfGfj041tHBYkX9'}
        )
        if response.json()['message'] != 'success':
            print('Track ' + table + ' failed!')
            print(response.json())

    response = requests.post(
        'https://hasura.' + subdomain + '.duckdns.org/v1/query',
        json={
            "type": "add_remote_schema",
            "args": {
                "name": "django",
                "definition": {
                    "url": "https://django." + subdomain + ".duckdns.org/graphql/",
                    # "headers": [{"name": "X-Server-Request-From", "value": "Hasura"}],
                    "forward_client_headers": True,
                    "timeout_seconds": 60
                },
            },
        },
        headers={'x-hasura-admin-secret': 'eDfGfj041tHBYkX9'}
    )
    if response.json()['message'] != 'success':
        print('Add Remote Schema failed!')
        print(response.json())
    return HttpResponse('Finished All Init Actions')
