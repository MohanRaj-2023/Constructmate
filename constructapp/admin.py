from django.contrib import admin
from constructapp.models import (Admin,customer_details,Project_manager,project_details,qda_analysis,High_quality_materialCost,
                      Standard_quality_materialCost,ConstructionData,
                      manager_messenger_to_vendor,vendor_details,Materials_report_qc,
                      Quality_checker,manager_to_quality,QualityAnalysis,quality_to_manager,vendor_to_manager,
                      Message,Medium_quality_materialCost)


#DJANGO_ADMIN_USER_NAME: Raj
#DJANGO_ADMIN_PASSWORD: raj@123

# Register your models here.
admin.site.register(Admin),
admin.site.register(customer_details),
admin.site.register(Project_manager),
admin.site.register(project_details),
admin.site.register(qda_analysis),
admin.site.register(High_quality_materialCost),
admin.site.register(Standard_quality_materialCost),
admin.site.register(ConstructionData),
admin.site.register(manager_messenger_to_vendor),
admin.site.register(vendor_details),
admin.site.register(Materials_report_qc),
admin.site.register(Quality_checker),
admin.site.register(manager_to_quality),
admin.site.register(QualityAnalysis),
admin.site.register(quality_to_manager),
admin.site.register(vendor_to_manager),
admin.site.register(Message),
admin.site.register(Medium_quality_materialCost),

#Quality check completed successfully. Materials have passed all inspections.
#Quality check failed. Materials did not meet the required standards and need to be revised.


