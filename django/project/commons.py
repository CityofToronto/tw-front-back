import datetime
from djangoAPI.models import *
from project.models import *
from djangoAPI.graphql.projects import *
from django.shortcuts import render, get_object_or_404, get_list_or_404


def user_projects(usr_id):
    """
    Display all projects that are the user belongs to
    """
    usr_obj = UserTbl.objects.get(pk=usr_id)
    usr_projs = []
    links = UserProjectLinkTbl.objects.filter(user_id=usr_id)
    # usr_role = DesignProjectHumanRoleTypeTbl.objects.get(pk=usr_obj.role_id)
    for link in links:
        proj = DesignProjectTbl.objects.get(pk=link.project_id)
        proj = UserProjects(id=proj.id, project_number=proj.id,
                            project_name=proj.name, user_role_id=usr_obj.role_id)
        usr_projs.append(proj)
    return usr_projs


def project_details(proj_id):
    """
    Display the Details of a Project
    """
    proj = get_object_or_404(DesignProjectTbl, pk=proj_id)
    disp_proj_detail = ProjectDetails()
    disp_proj_detail.__dict__ = proj.__dict__.copy()
    disp_proj_detail.bus_unit_name = proj.op_bus_unit.name
    disp_proj_detail.start_date = proj.planned_date_range.lower
    disp_proj_detail.end_date = proj.planned_date_range.upper
    # put in placeholder data for contacts in case nothing is found
    disp_proj_detail.project_manager = 'Does Not Exist'
    disp_proj_detail.project_manager_email = 'example@example.ca'
    disp_proj_detail.key_business_unit_contact = 'Does Not Exist'
    disp_proj_detail.key_business_unit_contact_email = 'example@example.ca'
    disp_proj_detail.asset_data_steward = 'Does Not Exist'
    disp_proj_detail.asset_data_steward_email = 'example@example.ca'
    persons = get_list_or_404(UserTbl, role_id='b')
    for person in persons:
        try:
            links = UserProjectLinkTbl.objects.filter(user_id=person.pk)
            for link in links:
                if link.project_id == proj.id:
                    disp_proj_detail.project_manager = person.get_full_name()
                    disp_proj_detail.project_manager_email = person.auth_user.email
                    break
        except Exception:
            pass
        persons = get_list_or_404(UserTbl, role_id='c')
    for person in persons:
        try:
            links = UserProjectLinkTbl.objects.filter(user_id=person.pk)
            for link in links:
                if link.project_id == proj.id:
                    disp_proj_detail.key_business_unit_contact = person.get_full_name()
                    disp_proj_detail.key_business_unit_contact_email = person.auth_user.email
                    break
        except Exception:
            pass
        persons = get_list_or_404(UserTbl, role_id='d')
    for person in persons:
        try:
            links = UserProjectLinkTbl.objects.filter(user_id=person.pk)
            for link in links:
                if link.project_id == proj.id:
                    disp_proj_detail.asset_data_steward = person.get_full_name()
                    disp_proj_detail.asset_data_steward_email = person.auth_user.email
                    break
        except Exception:
            pass
    return disp_proj_detail


def project_phases(project_id):
    """
    Returns all construction phases associated with a design project
    """
    result = []
    objs = list(ConstructionPhaseTbl.objects.filter(
        design_project=project_id))
    for obj in objs:
        new_obj = ConstructionPhases()
        new_obj.__dict__ = obj.__dict__.copy()
        new_obj.start_date = obj.planned_date_range.lower
        new_obj.end_date = obj.planned_date_range.upper
        result.append(new_obj)
    return result


def construction_phase(phase_id):
    """
    Return one construction phase by id
    """
    obj = ConstructionPhaseTbl.objects.get(pk=phase_id)
    new_obj = ConstructionPhases()
    new_obj.__dict__ = obj.__dict__.copy()
    new_obj.start_date = obj.planned_date_range.lower
    new_obj.end_date = obj.planned_date_range.upper
    return new_obj


def project_role(request, project_id):
    """
    Returns one project for editing roles
    """
    usr_id = request.user.id
    usr_obj = UserTbl.objects.get(pk=usr_id)
    link = UserProjectLinkTbl.objects.filter(user_id=usr_id).get(project_id=project_id)
    # usr_role = DesignProjectHumanRoleTypeTbl.objects.get(pk=usr_obj.role_id)
    proj = link.project
    proj = UserProjects(id=proj.id, project_number=proj.id,
                        project_name=proj.name, user_role_id=usr_obj.role_id)
    return proj


def update_project_role(user_id, data):
    """
    change the role of the user
    """
    # Currently there is a AllHumanRoleType and a UserRole table,
    # changing the AllHumanRoleType changes the role for all projects
    # the user is a part of, while changing the UserRole would be project
    # specific there are no specs for UserRole
    # TODO


def update_design_project(user_id, new):
    """
    sort through the data and updates as necessary
    compares against the old project details
    """
    old = project_details(new.get('id'))
    for key, value in new.__dict__.items():
        if old.__dict__[key] != value:
            print(key, value)
