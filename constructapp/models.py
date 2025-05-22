from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Create your models here.

class Admin(models.Model):
    user_name=models.CharField(max_length=50)
    password=models.CharField(max_length=50)

    def __str__(self):
        return self.user_name

class customer_details(models.Model):
    Name=models.CharField(max_length=50)
    Contact=models.CharField(max_length=15)
    Address = models.TextField(null=True)
    Email=models.EmailField(max_length=50)
    Password=models.CharField(max_length=500)

    def __str__(self):
        return self.Name



class Project_manager(models.Model):
    Name=models.CharField(max_length=50)
    Contact=models.CharField(max_length=15)
    Email=models.EmailField(max_length=50)
    Password=models.CharField(max_length=500)
    is_approve = models.CharField(max_length=10,default='pending')

    def __str__(self):
        return self.Name

class vendor_details(models.Model):
    Name=models.CharField(max_length=50)
    Contact=models.CharField(max_length=15)
    Email=models.EmailField(max_length=50)
    Password=models.CharField(max_length=500)
    is_approve = models.CharField(max_length=10,default='pending')

    def __str__(self):
        return self.Name

class Quality_checker(models.Model):
    Name = models.CharField(max_length=50)
    Contact = models.CharField(max_length=15)
    Email = models.EmailField(max_length=50)
    Password = models.CharField(max_length=500)
    is_approve = models.CharField(max_length=10,default='pending')


    def __str__(self):
        return self.Name

class project_details(models.Model):
    Customer = models.ForeignKey(customer_details, on_delete=models.CASCADE)
    Building_type=models.CharField(max_length=50)
    Land_area=models.FloatField()
    Soil_type=models.CharField(max_length=50)
    Soil_condition=models.CharField(max_length=50)
    Materials=models.CharField(max_length=500)
    Expectation=models.TextField()
    Project_manager=models.CharField(max_length=100,null=True)
    cost_report=models.FileField(null=True)
    materials_report=models.FileField(null=True,blank=True)
    Customer_confirmation=models.CharField(max_length=50,null=True)
    Status=models.TextField(null=True,blank=True)
    Reason=models.TextField(null=True,blank=True)
    vendor=models.CharField(max_length=100,null=True)
    supply_id = models.IntegerField(null=True)
    quality_checker=models.CharField(max_length=100,null=True)
    quality_check_report=models.FileField(null=True)
    Address = models.TextField(null=True)

    def __str__(self):
        return f"Project: {self.id}"

class qda_analysis(models.Model):
    project_manager = models.ForeignKey(Project_manager, on_delete=models.CASCADE)
    expectation=models.TextField()
    insights = models.TextField(blank=True, null=True)  # This will store the analysis result
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"QDA Analysis {self.id} for Project Manager {self.project_manager.Name}"

#marerials required
class ConstructionData(models.Model):
    Customer = models.ForeignKey(customer_details, on_delete=models.CASCADE)
    land_area = models.FloatField()  # in square meters or feet
    materials_expectations=models.CharField(max_length=100, null=True)
    material_quantities = models.JSONField(null=True, blank=True)  # Stores the estimated quantities of materials
    total_cost = models.FloatField(null=True, blank=True)  # Total estimated cost of materials
    def __str__(self):
        return f"Construction {self.id} - Area: {self.land_area} sq.m."

#materials_cost
class High_quality_materialCost(models.Model):
    material_name = models.CharField(max_length=100)
    cost_per_unit = models.FloatField()  # Cost per unit (e.g., per kg, per cubic meter)
    units = models.CharField(max_length=50,null=True)

    def __str__(self):
        return f"{self.material_name} - {self.cost_per_unit} INR/unit"


class Standard_quality_materialCost(models.Model):
    material_name = models.CharField(max_length=100)
    cost_per_unit = models.FloatField()  # Cost per unit (e.g., per kg, per cubic meter)
    units= models.CharField(max_length=50,null=True)

    def __str__(self):
        return f"{self.material_name} - {self.cost_per_unit} INR/unit"


class Medium_quality_materialCost(models.Model):
    material_name = models.CharField(max_length=100)
    cost_per_unit = models.FloatField()  # Cost per unit (e.g., per kg, per cubic meter)
    units = models.CharField(max_length=50,null=True)

    def __str__(self):
        return f"{self.material_name} - {self.cost_per_unit} INR/unit"


#mnager_messenger_to_vendor
class manager_messenger_to_vendor(models.Model):
    sender = models.ForeignKey(Project_manager, on_delete=models.CASCADE, related_name='manager_vendor')
    receiver = models.ForeignKey(vendor_details, on_delete=models.CASCADE, related_name='vendor')
    subject=models.CharField(null=True,max_length=100)
    file = models.FileField(null=True)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message - {self.id}"



#vendor reports to Qc
class Materials_report_qc(models.Model):
    vendor= models.ForeignKey(vendor_details, on_delete=models.CASCADE)
    project_id=models.IntegerField()
    cement_grade = models.CharField(max_length=10)
    cement_quantity = models.CharField(max_length=10)
    sand_grade = models.CharField(max_length=10)
    sand_quantity = models.CharField(max_length=10)
    aggregate_grade = models.CharField(max_length=10)
    aggregate_quantity = models.CharField(max_length=10)
    steel_grade = models.CharField(max_length=10)
    steel_quantity = models.CharField(max_length=10)
    paint_grade = models.CharField(max_length=10)
    paint_quantity = models.CharField(max_length=10)
    bricks_grade = models.CharField(max_length=10)
    bricks_quantity = models.CharField(max_length=10)
    tiles_grade = models.CharField(max_length=10)
    tiles_quantity = models.CharField(max_length=10)
    insulation_grade = models.CharField(max_length=10, blank=True, null=True)
    insulation_quantity = models.CharField(max_length=10, blank=True, null=True)
    adhesive_grade = models.CharField(max_length=10)
    adhesive_quantity = models.CharField(max_length=10)
    concrete_blocks_grade = models.CharField(max_length=10)
    concrete_block_quantity = models.CharField(max_length=10)
    electrical_wire_grade = models.CharField(max_length=10)
    electrical_wire_quantity = models.CharField(max_length=10)
    pipes_grade = models.CharField(max_length=10)
    pipes_quantity = models.CharField(max_length=10)
    wood_grade = models.CharField(max_length=10)
    wood_quantity = models.CharField(max_length=10)
    gravel_grade = models.CharField(max_length=10)
    gravel_quantity = models.CharField(max_length=10)


#manager_to_quality
class manager_to_quality(models.Model):
    sender = models.ForeignKey(Project_manager, on_delete=models.CASCADE, related_name='project_manager')
    receiver = models.ForeignKey(Quality_checker, on_delete=models.CASCADE, related_name='quality_checker')
    subject=models.CharField(null=True,max_length=100)
    file = models.FileField(null=True)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message - {self.id}"


#vendor_to_manager
class vendor_to_manager(models.Model):
    sender = models.ForeignKey(vendor_details, on_delete=models.CASCADE, related_name='vendor_sender')
    receiver = models.ForeignKey(Project_manager, on_delete=models.CASCADE, related_name='receiver_project_manager')
    subject=models.CharField(null=True,max_length=100)
    file = models.FileField(null=True)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

#quality_to_manager
class quality_to_manager(models.Model):
    sender = models.ForeignKey(Quality_checker, on_delete=models.CASCADE, related_name='quality_sender')
    receiver = models.ForeignKey(Project_manager, on_delete=models.CASCADE, related_name='project_manager_receiver')
    subject=models.CharField(null=True,max_length=100)
    file = models.FileField(null=True)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message - {self.id}"

class QualityAnalysis(models.Model):
    material_report = models.OneToOneField(Materials_report_qc, on_delete=models.CASCADE)
    cement_quality = models.CharField(max_length=50)
    sand_quality = models.CharField(max_length=50)
    aggregate_quality = models.CharField(max_length=50)
    steel_quality = models.CharField(max_length=50)
    paint_quality = models.CharField(max_length=50)
    bricks_quality = models.CharField(max_length=50)
    tiles_quality = models.CharField(max_length=50)
    insulation_quality = models.CharField(max_length=50,blank=True, null=True)
    adhesive_quality = models.CharField(max_length=50)
    concrete_quality = models.CharField(max_length=50)
    electrical_wire_quality = models.CharField(max_length=50)
    pipes_quality = models.CharField(max_length=50)
    wood_quality = models.CharField(max_length=50)
    gravel_quality = models.CharField(max_length=50)
    materials_quality = models.TextField(null=True)
    sufficient_materials = models.TextField(null=True)
    analysis_date = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    # Generic sender
    sender_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='sender_type')
    sender_object_id = models.PositiveIntegerField()
    sender = GenericForeignKey('sender_content_type', 'sender_object_id')

    # Generic receiver
    receiver_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='receiver_type')
    receiver_object_id = models.PositiveIntegerField()
    receiver = GenericForeignKey('receiver_content_type', 'receiver_object_id')

    file=models.FileField(null=True)
    subject = models.CharField(max_length=100, null=True)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender} to {self.receiver}"