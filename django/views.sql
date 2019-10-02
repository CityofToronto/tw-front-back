create or replace view temp_asset_initial_final as
SELECT ba.id, 
coalesce(mea.final_project_asset_role_id_id, na.final_project_asset_role_id_id, ea.initial_project_asset_role_id_id) as final_role_id, 
br.parent_id_id as parent_id,
coalesce(ea.initial_project_asset_role_id_id) as initial_role_number
FROM public."djangoAPI_projectassetrecordtbl" as ba
full outer JOIN public."djangoAPI_predesignreconciledassetrecordtbl" as ea
ON ba.id=ea.projectassetrecordtbl_ptr_id
full outer join public."djangoAPI_existingassetmovedbyprojecttbl" as mea
on ba.id=mea.predesignreconciledassetrecordtbl_ptr_id
full outer join public."djangoAPI_newassetdeliveredbyprojecttbl" as na
on ba.id=na.projectassetrecordtbl_ptr_id
full outer join public."djangoAPI_projectassetrolerecordtbl" as br
on ea.initial_project_asset_role_id_id=br.id
where ea.designer_planned_action_type_tbl_id<>2
;

create or replace view role_asset as
select br.id as role_id,
br.updatable_role_number as role_number,
parent_id as parent,
br1.updatable_role_number as asset_number
from public."djangoAPI_projectassetrolerecordtbl" as br
full outer join temp_asset_initial_final as aif
on aif.final_role_id = br.id
full outer join public."djangoAPI_projectassetrolerecordtbl" as br1
on aif.initial_role_number = br1.id;

create or replace view reconciliation_view as
select 
r.id, r.updatable_role_number as role_number,
r.role_name as role_name,
r.parent_id_id as parent,
r.project_tbl_id as project_id,
r.entity_exists as role_exists,
r.missing_from_registry as role_missing_from_registry,
a.id as asset_id,
a.asset_serial_number as asset_serial_number,
a.entity_exists as asset_exists,
a.missing_from_registry as asset_missing_from_registry
from (
public."djangoAPI_projectassetrolerecordtbl" as br
right join public."djangoAPI_predesignreconciledrolerecordtbl" as pr
on (br.id=pr.projectassetrolerecordtbl_ptr_id)) as r
left join (
public."djangoAPI_predesignreconciledassetrecordtbl" as pa 
left join public."djangoAPI_projectassetrecordtbl" as ba 
on (pa.projectassetrecordtbl_ptr_id=ba.id)) as a 
on (r.id=a.initial_project_asset_role_id_id)
--where a.designer_planned_action_type_tbl_id<>2
;

create or replace view unassigned_assets as
select ba.id as id, ba.asset_serial_number as asset_serial_number
from public."djangoAPI_predesignreconciledassetrecordtbl" as pa
left join public."djangoAPI_projectassetrecordtbl" as ba
on pa.projectassetrecordtbl_ptr_id=ba.id
where pa.initial_project_asset_role_id_id is null and pa.designer_planned_action_type_tbl_id<>2