BEGIN;
SELECT setval(pg_get_serial_sequence('"djangoAPI_Sites"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "djangoAPI_Sites";
SELECT setval(pg_get_serial_sequence('"djangoAPI_DBTbls"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "djangoAPI_DBTbls";
SELECT setval(pg_get_serial_sequence('"djangoAPI_UserType"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "djangoAPI_UserType";
SELECT setval(pg_get_serial_sequence('"djangoAPI_UserGroupNameTbl"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "djangoAPI_UserGroupNameTbl";
SELECT setval(pg_get_serial_sequence('"djangoAPI_SuperDesignProjectTbl"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "djangoAPI_SuperDesignProjectTbl";
SELECT setval(pg_get_serial_sequence('"djangoAPI_DesignProjectTbl"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "djangoAPI_DesignProjectTbl";
SELECT setval(pg_get_serial_sequence('"djangoAPI_DesignProjectHumanRoleTbl"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "djangoAPI_DesignProjectHumanRoleTbl";
SELECT setval(pg_get_serial_sequence('"djangoAPI_DesignStageTbl"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "djangoAPI_DesignStageTbl";
SELECT setval(pg_get_serial_sequence('"djangoAPI_ConstructionPhaseTbl"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "djangoAPI_ConstructionPhaseTbl";  
SELECT setval(pg_get_serial_sequence('"djangoAPI_ConstructionPhaseHumanRoleTbl"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "djangoAPI_ConstructionPhaseHumanRoleTbl";
SELECT setval(pg_get_serial_sequence('"djangoAPI_ConstructionStageTbl"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "djangoAPI_ConstructionStageTbl";  
SELECT setval(pg_get_serial_sequence('"djangoAPI_ImportedSpatialSiteTbl"','spatial_site_id'), coalesce(max("spatial_site_id"), 1), max("spatial_site_id") IS NOT null) FROM "djangoAPI_ImportedSpatialSiteTbl";
SELECT setval(pg_get_serial_sequence('"djangoAPI_MasterRoleNumbersTbl"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "djangoAPI_MasterRoleNumbersTbl";  
SELECT setval(pg_get_serial_sequence('"djangoAPI_ClonedAssetAndRoleInRegistryTbl"','mtoi'), coalesce(max("mtoi"), 1), max("mtoi") IS NOT null) FROM "djangoAPI_ClonedAssetAndRoleInRegistryTbl";
SELECT setval(pg_get_serial_sequence('"djangoAPI_UserAccessLinkTbl"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "djangoAPI_UserAccessLinkTbl";        
SELECT setval(pg_get_serial_sequence('"djangoAPI_AccessProfileDefinitionTbl"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "djangoAPI_AccessProfileDefinitionTbl";
SELECT setval(pg_get_serial_sequence('"djangoAPI_UserProjectLinkTbl"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "djangoAPI_UserProjectLinkTbl";      
SELECT setval(pg_get_serial_sequence('"djangoAPI_ProjectAssetRoleRecordTbl"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "djangoAPI_ProjectAssetRoleRecordTbl";
SELECT setval(pg_get_serial_sequence('"djangoAPI_ProjectAssetRecordTbl"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "djangoAPI_ProjectAssetRecordTbl";
SELECT setval(pg_get_serial_sequence('"djangoAPI_AssetClassificationTbl"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "djangoAPI_AssetClassificationTbl";
SELECT setval(pg_get_serial_sequence('"auth_permission"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "auth_permission";
SELECT setval(pg_get_serial_sequence('"auth_group_permissions"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "auth_group_permissions";
SELECT setval(pg_get_serial_sequence('"auth_group"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "auth_group";
SELECT setval(pg_get_serial_sequence('"auth_user_groups"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "auth_user_groups";
SELECT setval(pg_get_serial_sequence('"auth_user_user_permissions"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "auth_user_user_permissions";
SELECT setval(pg_get_serial_sequence('"auth_user"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "auth_user";
COMMIT;