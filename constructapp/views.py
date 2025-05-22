from django.shortcuts import render,redirect,HttpResponse,reverse
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password


from constructapp.models import (Admin,customer_details,Project_manager,project_details,qda_analysis,ConstructionData,
                                High_quality_materialCost,Standard_quality_materialCost,vendor_details,Materials_report_qc,
                                Quality_checker,QualityAnalysis,Message,Medium_quality_materialCost)


#For Message
from django.contrib.contenttypes.models import ContentType


from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
#from django.contrib.auth.decorators import login_required

#QDA requirements

import re
#import nltk
#nltk.download('punkt_tab')

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

#Theil-sen requirements
import numpy as np
from sklearn.linear_model import TheilSenRegressor


# Create your views here.
def home(request):
    return render(request,'index.html')


def admin_login(request):
    if request.method=='POST':
        get_username=request.POST.get('username')
        get_password=request.POST.get('password')
        if get_username == 'admin' and get_password == 'admin@123':
            messages.success(request,'Welcome Admin!')
            return redirect('admin_interface')

        else:
            messages.error(request,'Invalid Credentials')

    return render(request,'admin_login.html')

def admin_interface(request):
    return render(request,'admin_interface.html')

def admin_about(request):
    return render(request,'admin_about.html')
def admin_home(request):
    return render(request,'admin_home.html')

def customer_signup(request):
    if request.method=='POST':
        user_name=request.POST.get('Name')
        user_contact=request.POST.get('contact')
        user_address=request.POST.get('address')
        user_email=request.POST.get('mail')
        user_password=request.POST.get('password')
        hash_password=make_password(user_password)
        db=customer_details.objects.create(
            Name=user_name,
            Contact=user_contact,
            Address=user_address,
            Email=user_email,
            Password=hash_password
        )
        db.save()
        return redirect('customer_login')
    return render(request,'customer_signup.html')


def customer_login(request):
    if request.method == 'POST':
        usermail = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Check if the email exists in the database
            customer = customer_details.objects.get(Email=usermail)
            # If the email exists, check if the password matches
            print('PASSWORD:', customer.Password)
            if check_password(password, customer.Password):
                request.session['customer_id'] = customer.id  # Store manager ID in session
                return redirect('customer_page')
            else:

                messages.error(request, 'Invalid Credentials')
                return redirect('customer_login')

        except customer_details.DoesNotExist:
            messages.error(request, 'Invalid Credentials')
            return redirect('customer_login')



    return render(request, 'customer_login.html')


def customer_interface(request):
    return render(request,'customer_interface.html')

def customer_home(request):
    return render(request,'customer_home.html')
def view_my_projects(request):
    customer_id=request.session.get('customer_id')
    customer=customer_details.objects.get(id=customer_id)
    try:
      project=project_details.objects.get(Customer=customer)
      print('PROJECT:',project.Status)
      if project.Status!='Customer Declined The Analysis Report' and project.Status != 'Project Completion Confirmed':
        return render(request,'view_my_projects.html',{'project':project})
      else:
          return render(request, 'view_my_projects.html')
    except Exception as error:
        return render(request, 'view_my_projects.html')
def customer_message_page(request,Content):
        Data=Content
        return render(request,'customer_msg.html',{'messages':Data})



def customer_message(request):
        Customer_id=request.session.get('customer_id')
        customer=customer_details.objects.get(id=Customer_id)
        customer_content_type=ContentType.objects.get_for_model(customer_details)
        my_msg=Message.objects.filter(receiver_content_type=customer_content_type,
                                      receiver_object_id=customer.id).order_by('-timestamp')
        return render(request,'customer_msg.html',{'messages':my_msg})

def customer_to_manager(request):
    if request.method == 'POST':
        customer_id = request.session.get('customer_id')
        receiver = request.POST.get('to')
        try:
            Sender = customer_details.objects.get(id=customer_id)
        except customer_details.DoseNotExist:
            messages.error(request,'Customer Not Exist...')
            return redirect('customer_to_manager')
        try:
            Receiver = Project_manager.objects.get(Name=receiver)
        except Project_manager.DoesNotExist:
            messages.error(request, 'Project_manager not exists...')
            return redirect('customer_to_manager')


        Subject = request.POST.get('subject')
        File = request.FILES.get('report')
        Description = request.POST.get('message')

        # Get the ContentType of the sender and receiver
        customer_content_type = ContentType.objects.get_for_model(customer_details)
        manager_content_type = ContentType.objects.get_for_model(Project_manager)

        # Retrieve actual sender and receiver instances
        sender = customer_details.objects.get(id=Sender.id)
        receiver = Project_manager.objects.get(id=Receiver.id)

        db = Message.objects.create(
        sender_content_type=customer_content_type,
        sender_object_id=sender.id,
        receiver_content_type=manager_content_type,
        receiver_object_id=receiver.id,
        subject=Subject,
        file=File,
        description=Description
        )
        db.save()
        try:
            project_db = project_details.objects.get(Customer=Sender)
        except project_details.DoesNotExist:
            messages.error(request,'Start you project, No project exist')
            return redirect('customer_to_manager')

        project_db.cost_report = File
        project_db.save()
        messages.success(request, 'Message sent......!')
        return redirect('customer_to_manager')

    return render(request, 'customer_to_manager.html')


def view_customer_message(request,message_id):
    message=Message.objects.get(id=message_id)
    print("Message:",message)
    return render(request,'view_customer_message.html',{'message':message})

#Project_Manager

def manager_signup(request):
    if request.method=='POST':
        user_name=request.POST.get('Name')
        user_contact=request.POST.get('contact')
        user_email=request.POST.get('mail')
        user_password=request.POST.get('password')
        hash_password=make_password(user_password)
        db=Project_manager.objects.create(
            Name=user_name,
            Contact=user_contact,
            Email=user_email,
            Password=hash_password
        )
        db.save()
        return redirect('manager_login')
    return render(request,'manager_signup.html')


#Manager_Authentication
def manager_login(request):
    if request.method=='POST':
        usermail=request.POST.get('email')
        password=request.POST.get('password')
        try:
            manager= Project_manager.objects.get(Email=usermail)

            if check_password(password,manager.Password):
                request.session['manager_id'] = manager.id  # Store manager ID in session
                if manager.is_approve == 'pending':
                    return redirect('manager_pending')
                elif manager.is_approve == 'declined':
                    return redirect('manager_declined')
                else:
                    #messages.success(request, 'Welcome Project Manager!')
                    return redirect('manager_interface')
            else:
                messages.error(request,'Invalid Credentials')
                return redirect('manager_login')
        except Project_manager.DoesNotExist:
            messages.error(request, 'Invalid Credentials')
            return redirect('manager_login')

    return render(request,'manager_login.html')

def manager_pending(request):
    return render(request,'manager_pending.html')

def manager_declined(request):
    return render(request,'manager_declined.html')
def manager_interface(request):
    return render(request,'manager_interface.html')

def manager_home(request):
    return render(request,'manager_home.html')
def manager_signup_page(request):
    return render(request,'manager_signup.html')

def manager_message(request):
        Manager_id=request.session.get('manager_id')
        manager=Project_manager.objects.get(id=Manager_id)
        manager_content_type=ContentType.objects.get_for_model(Project_manager)
        my_msg = Message.objects.filter(receiver_content_type=manager_content_type,
              receiver_object_id=manager.id).order_by('-timestamp')

        return render(request,'manager_msg.html',{'messages':my_msg})



#project_form
def project_form(request,Customer_ID):
    return render(request,'project_form.html',{'Customer_id':Customer_ID})

def initiation_form_submit(request):
    if request.method=='POST':
        Customer_id=request.session.get('customer_id')
        Customer_details=customer_details.objects.get(id=Customer_id)
        getbuilding_type=request.POST.get('Building')
        getLand_area=request.POST.get('land_area')
        getSoil_type=request.POST.get('soil_type')
        get_custom_soil_type=request.POST.get('custom_soil_type')
        getSoil_condition=request.POST.get('soil_condition')
        get_custom_soil_condition=request.POST.get('custom_soil_condition')
        getMaterials=request.POST.get('materials')
        getExpectation=request.POST.get('expectation')

        db=project_details(Address = Customer_details.Address)
        db.Customer = Customer_details
        db.Building_type = getbuilding_type
        db.Land_area = getLand_area

        if getSoil_type=='Other':
            db.Soil_type = get_custom_soil_type
        else:
            db.Soil_type = getSoil_type
        if getSoil_condition=='Other':
            db.Soil_condition = get_custom_soil_condition
        else:
            db.Soil_condition = getSoil_condition

        db.Materials = getMaterials
        db.Expectation = getExpectation
        db.Status='Project Initiation Form Submitted'
        db.save()
       # return redirect('manager',project_id=Customer_id)
        return render(request,'project_form_submitted.html',{'id':Customer_id})
    return render(request,'project_form.html')


#Projects
def projects(request):
    try:
        manager_id=request.session.get('manager_id')
        manager=Project_manager.objects.get(id=manager_id)
        Projects = project_details.objects.filter(Project_manager = manager.Name )
        project_list=[]

        for project in Projects:
             if (project.cost_report == None or project.Status =='Customer Accepted The Updated Project Details' or project.Status== 'Project Manager Assigned'):
                 project_list.append(project)
             else:
                return render(request, 'projects.html')
        return render(request, 'projects.html', {'projects': project_list})
    except Exception as error:
        return render(request, 'projects.html')

def view_project(request,project_id):
    Projects = project_details.objects.get(id=project_id)
    return render(request,'view_project.html',{'project':Projects})

def edit_project_details(request,project_id):
    project=project_details.objects.get(id=project_id)
    return render(request,'edit_project_details.html',{'project':project})

def manager_to_customer_update(request,project_id):
    if request.method=='POST':
        project=project_details.objects.get(id=project_id)

        getbuilding_type = request.POST.get('Building_Type')
        getLand_area = request.POST.get('Land_Area')
        getSoil_type = request.POST.get('Soil_type')
        getSoil_condition = request.POST.get('Soil_condition')
        getMaterials = request.POST.get('materials')
        getExpectation = request.POST.get('Expectation')

        project.Building_type =getbuilding_type
        project.Land_area=getLand_area
        project.Soil_type=getSoil_type
        project.Soil_condition=getSoil_condition
        project.Materials=getMaterials
        project.Expectation=getExpectation

        customer=project.Customer.Name

        Sender_id=request.session.get('manager_id')
        Sender=Project_manager.objects.get(id=Sender_id)
        Receiver=customer_details.objects.get(Name=customer)

        Sender_type=ContentType.objects.get_for_model(Project_manager)
        Receiver_type=ContentType.objects.get_for_model(customer_details)
        db=Message.objects.create(
            sender_content_type=Sender_type,
            sender_object_id=Sender.id,
            receiver_content_type=Receiver_type,
            receiver_object_id=Receiver.id,
            subject='Update In Project Details',
            description='We have updated the details of your project to better align with your requirements. Please review the changes and confirm your approval'
        )
        db.save()
        project.Status='Project Details Updated and Sent for Customer Review'
        project.save()
        return render(request,'update_landing.html',{'project_id':project_id})

    return render(request,'manager_to_customer_update')

def view_updated_details(request,customer_id):
    try:
        customer=customer_details.objects.get(id=customer_id)
    except customer_details.DoesNotExist:
        return HttpResponse('Customer Not Exist...')
    try:
        project=project_details.objects.get(Customer=customer)
        return render(request, 'view_updated_details.html', {'project': project})

    except project_details.DoesNotExist:
        data = 'This project is deleted.'
        return render(request,'view_updated_details.html',{'DoesNotExist':data})

def analysis(request,project_id):
    return render(request,'analysispage.html',{'project_id':project_id})

#QDA Analysis

def qda_analysis_page(request,project_id):
    return render(request,'qda_analysis.html',{'project_id':project_id})
def QDA_analysis(request,content):
    return render(request,'qda_analysis.html',{'Data':content})

def get_expectation(request,project_id):
        Customer=project_details.objects.get(id=project_id)
        Expectation_data=Customer.Expectation
        redirect_url = reverse('QDA_analysis', kwargs={'content': Expectation_data})
        return redirect(redirect_url)


def categorize_text(tokens):
    categories = {
        'high_quality': {
            'keywords': ['premium', 'luxury', 'high-end', 'superior', 'top-notch'],
            'sentence': 'The customer emphasizes high-quality materials.'
        },
        'budget': {
            'keywords': ['affordable', 'cheap', 'budget', 'economical', 'cost-effective'],
            'sentence': 'The customer is focused on budget-friendly solutions.'
        },
        'durable': {
            'keywords': ['long-lasting', 'durable', 'sturdy', 'resilient', 'robust'],
            'sentence': 'The customer values durable and sturdy materials.'
        },
        'eco_friendly': {
            'keywords': ['green', 'sustainable', 'eco-friendly', 'environmental', 'renewable'],
            'sentence': 'The customer prefers environmentally sustainable materials.'
        },
        'modern_design': {
            'keywords': ['contemporary', 'modern', 'sleek', 'minimalist', 'cutting-edge'],
            'sentence': 'The customer desires a modern and contemporary design.'
        },
        'traditional_design': {
            'keywords': ['classic', 'traditional', 'vintage', 'rustic', 'timeless'],
            'sentence': 'The customer prefers a traditional and classic design.'
        },
        'energy_efficient': {
            'keywords': ['energy-saving', 'efficient', 'low-energy', 'green', 'sustainable'],
            'sentence': 'The customer prioritizes energy-efficient solutions.'
        },
        'quick_build': {
            'keywords': ['fast', 'quick', 'rapid', 'swift', 'expedient'],
            'sentence': 'The customer wants a quick and expedient construction process.'
        },
        'customizable': {
            'keywords': ['tailored', 'custom', 'bespoke', 'personalized', 'adaptable'],
            'sentence': 'The customer is looking for customizable solutions.'
        },
        'low_maintenance': {
            'keywords': ['maintenance-free', 'low-maintenance', 'easy-care', 'hassle-free', 'durable'],
            'sentence': 'The customer prefers low-maintenance materials and designs.'
        },
        'aesthetic': {
            'keywords': ['beautiful', 'aesthetic', 'pleasing', 'attractive', 'appealing'],
            'sentence': 'The customer focuses on aesthetic appeal.'
        },
        'spacious': {
            'keywords': ['roomy', 'spacious', 'large', 'wide', 'expansive'],
            'sentence': 'The customer wants a spacious and roomy design.'
        },
        'privacy': {
            'keywords': ['private', 'secluded', 'isolated', 'quiet', 'exclusive'],
            'sentence': 'The customer values privacy and seclusion.'
        },
        'smart_home': {
            'keywords': ['automated', 'smart', 'connected', 'intelligent', 'high-tech'],
            'sentence': 'The customer is interested in smart home technology.'
        },
        'luxury_finishes': {
            'keywords': ['marble', 'granite', 'hardwood', 'luxury', 'high-end'],
            'sentence': 'The customer desires luxury finishes.'
        },
        'minimalist': {
            'keywords': ['simple', 'minimalist', 'clean', 'streamlined', 'uncluttered'],
            'sentence': 'The customer prefers a minimalist and clean design.'
        },
        'family_friendly': {
            'keywords': ['family', 'kids', 'child-safe', 'friendly', 'comfortable'],
            'sentence': 'The customer wants a family-friendly environment.'
        },
        'pet_friendly': {
            'keywords': ['pet', 'dog', 'cat', 'animal', 'friendly'],
            'sentence': 'The customer wants a pet-friendly design.'
        },
        'open_concept': {
            'keywords': ['open', 'flow', 'airy', 'spacious', 'unified'],
            'sentence': 'The customer prefers an open concept layout.'
        },
        'security': {
            'keywords': ['secure', 'safe', 'protected', 'guarded', 'alarm'],
            'sentence': 'The customer is concerned about security.'
        },
        'outdoor_space': {
            'keywords': ['garden', 'yard', 'patio', 'deck', 'outdoor'],
            'sentence': 'The customer desires ample outdoor space.'
        },
        'natural_light': {
            'keywords': ['bright', 'natural light', 'windows', 'sunlight', 'well-lit'],
            'sentence': 'The customer values natural light in the design.'
        },
        'cost_savings': {
            'keywords': ['cost-saving', 'economical', 'affordable', 'budget', 'inexpensive'],
            'sentence': 'The customer is looking for cost-saving measures.'
        },
        'innovative': {
            'keywords': ['innovative', 'creative', 'unique', 'cutting-edge', 'groundbreaking'],
            'sentence': 'The customer is looking for innovative solutions.'
        },
        'accessible': {
            'keywords': ['accessible', 'easy access', 'disabled-friendly', 'barrier-free', 'inclusive'],
            'sentence': 'The customer requires accessible features.'
        },
        'modular': {
            'keywords': ['modular', 'interchangeable', 'flexible', 'adaptable', 'customizable'],
            'sentence': 'The customer is interested in modular designs.'
        },
        'energy_saving': {
            'keywords': ['energy-efficient', 'low-energy', 'green', 'eco-friendly', 'sustainable'],
            'sentence': 'The customer prioritizes energy-saving solutions.'
        },
        'low_cost': {
            'keywords': ['inexpensive', 'affordable', 'budget', 'low-cost', 'economical'],
            'sentence': 'The customer is focused on keeping costs low.'
        },
        'sustainable': {
            'keywords': ['sustainable', 'green', 'eco-friendly', 'renewable', 'environmentally-friendly'],
            'sentence': 'The customer prefers sustainable materials and practices.'
        },
        'versatile': {
            'keywords': ['versatile', 'flexible', 'adaptable', 'multifunctional', 'convertible'],
            'sentence': 'The customer values versatility in design.'
        },
        'urban': {
            'keywords': ['city', 'urban', 'modern', 'metropolitan', 'contemporary'],
            'sentence': 'The customer is looking for an urban design.'
        },
        'rustic': {
            'keywords': ['rustic', 'country', 'natural', 'wooden', 'traditional'],
            'sentence': 'The customer prefers a rustic design.'
        },
        'high_performance': {
            'keywords': ['high-performance', 'efficient', 'top-tier', 'premium', 'high-grade'],
            'sentence': 'The customer desires high-performance materials.'
        },
        'environmentally_friendly': {
            'keywords': ['eco-friendly', 'green', 'sustainable', 'environmentally-conscious', 'recycled'],
            'sentence': 'The customer prefers environmentally friendly options.'
        },
        'comfort': {
            'keywords': ['comfortable', 'cozy', 'welcoming', 'homey', 'relaxing'],
            'sentence': 'The customer values comfort in the design.'
        },
        'fire_resistant': {
            'keywords': ['fire-resistant', 'fireproof', 'safe', 'secure', 'non-combustible'],
            'sentence': 'The customer requires fire-resistant materials.'
        },
        'waterproof': {
            'keywords': ['waterproof', 'water-resistant', 'durable', 'weatherproof', 'moisture-resistant'],
            'sentence': 'The customer values waterproofing in the design.'
        },
        'weather_resistant': {
            'keywords': ['weather-resistant', 'durable', 'weatherproof', 'tough', 'sturdy'],
            'sentence': 'The customer prefers weather-resistant materials.'
        },
        'noise_reduction': {
            'keywords': ['quiet', 'noise-cancelling', 'soundproof', 'insulated', 'peaceful'],
            'sentence': 'The customer is interested in noise reduction features.'
        },
        'seismic_resistant': {
            'keywords': ['earthquake-resistant', 'seismic', 'reinforced', 'sturdy', 'safe'],
            'sentence': 'The customer wants seismic-resistant construction.'
        },
        'adaptive_reuse': {
            'keywords': ['repurpose', 'reuse', 'adaptive', 'upcycle', 'convert'],
            'sentence': 'The customer is interested in adaptive reuse of materials.'
        },
        'artistic': {
            'keywords': ['artistic', 'creative', 'unique', 'handcrafted', 'personalized'],
            'sentence': 'The customer is looking for artistic elements in the design.'
        },
        'technology_integration': {
            'keywords': ['technology', 'integrated', 'smart', 'connected', 'automated'],
            'sentence': 'The customer wants technology integrated into the design.'
        },
        'cultural_significance': {
            'keywords': ['cultural', 'heritage', 'traditional', 'significant', 'historical'],
            'sentence': 'The customer values cultural significance in the design.'
        },
        'green_roof': {
            'keywords': ['green roof', 'eco-friendly', 'sustainable', 'vegetative', 'environmental'],
            'sentence': 'The customer is interested in a green roof.'
        },
        'luxury_living': {
            'keywords': ['luxury', 'high-end', 'premium', 'exclusive', 'elite'],
            'sentence': 'The customer desires a luxury and exclusive experience.'
        },
        'bedroom': {
               'keywords': ['bedroom', 'master bedroom', 'guest room', 'sleeping room'],
               'sentence': 'The customer requires {count} bedrooms.'
        },
        'bathroom': {
                'keywords': ['bathroom', 'washroom', 'restroom', 'ensuite', 'toilet'],
                'sentence': 'The customer requires {count} bathrooms.'
         },
        'kitchen': {
                'keywords': ['kitchen', 'cooking area', 'pantry'],
                'sentence': 'The customer emphasizes the importance of the kitchen.'
         },
        'living_room': {
                'keywords': ['living room', 'lounge', 'sitting room', 'family room'],
                'sentence': 'The customer is focused on the living room area.'
         },
        'dining_room': {
                'keywords': ['dining room', 'dining area', 'eating area'],
                'sentence': 'The customer highlights the dining room.'
        },
        'office': {
                'keywords': ['office', 'study', 'workroom', 'home office'],
                'sentence': 'The customer needs an office or study space.'
        },
        'garage': {
                'keywords': ['garage', 'carport', 'parking space'],
                 'sentence': 'The customer requires a garage or parking space.'
        },
        'balcony': {
                'keywords': ['balcony', 'terrace', 'veranda', 'porch'],
                'sentence': 'The customer wants a balcony or terrace.'
         }
 }

    categorized_data = []

    # Function to convert number words to digits
    def convert_words_to_numbers(text):
        # Define patterns for number words
        number_words = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
            'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19,
            'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
            'eighty': 80, 'ninety': 90
        }
        for word, number in number_words.items():
            text = re.sub(r'\b{}\b'.format(word), str(number), text)
        return text

    # Convert number words in tokens
    text = ' '.join(tokens)
    text = convert_words_to_numbers(text)
    tokens = text.split()

    for category, details in categories.items():
        count = 0
        for keyword in details['keywords']:
            # Look for phrases like "2 bedrooms" or "two bedrooms" in the text
            pattern = r'(\d+)\s+' + re.escape(keyword)
            matches = re.findall(pattern, ' '.join(tokens))
            if matches:
                count += sum(map(int, matches))

            # Check for number words
            pattern_words = r'(\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)\b)\s+' + re.escape(
                keyword)
            matches_words = re.findall(pattern_words, text)
            if matches_words:
                count += sum(w2n.word_to_num(word) for word in matches_words)

        if count > 0:
            # Format the sentence with the count
            categorized_data.append(details['sentence'].format(count=count))
        else:
            # If no count is found, check if the keyword itself is present
            if any(keyword in tokens for keyword in details['keywords']):
                categorized_data.append(details['sentence'].format(count=''))

    return categorized_data


def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token not in stop_words]
    lemmatizer = WordNetLemmatizer()
    processed_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens]
    return processed_tokens

def qda_result(request,qda_id):
      qda_data = qda_analysis.objects.get(id=qda_id)
      tokens = preprocess_text(qda_data.expectation)
      categorized_data = categorize_text(tokens)
      qda_data.insights=categorized_data
      qda_data.save()

      context = {'categorized_data': categorized_data}

      return render(request, 'qda_analysis.html', {'Qda_result':context})

def run_qda(request):

    if request.method=='POST':
            get_expectation=request.POST.get('expectation')
            # Retrieve the manager ID from the session
            session_manager_id = request.session.get('manager_id')
            try:
                get_manager_id = Project_manager.objects.get(id=session_manager_id)

                if get_manager_id.id == session_manager_id:
                    db=qda_analysis.objects.create(
                        project_manager=get_manager_id,
                        expectation=get_expectation,
                        insights = None
                        )
                    db.save()
                    return redirect('qda_result',qda_id=db.id)

            except ObjectDoesNotExist:
                return HttpResponse('Project Manager Not Exists...')


    return render(request,'qda_analysis.html')


#Theil-sen analysis
def theil_sen_analysis(request,project_id):
    return render(request,'theil-sen_page.html',{'project_id':project_id})


def get_land_area(request,project_id):
    project=project_details.objects.get(id=project_id)
    customer_name=project.Customer.Name
    customer=customer_details.objects.get(Name=customer_name)
    get_land_area=project.Land_area
    get_materials_expectation=project.Materials
    construction = (ConstructionData.objects.create(Customer=customer,land_area=get_land_area,materials_expectations=get_materials_expectation))
    construction.save()
    construction_id = construction.id
    return render(request,'theil-sen_page.html',{'customer':customer,'land_area':get_land_area,'construction_id':construction_id,
                 'materials_expectations':get_materials_expectation})


def train_theilsen_model():
    # Example updated training data (land area vs materials required)
    X = np.array([
        [500], [1000], [1500], [2000], [2500], [3000], [3500], [4000], [4500], [5000]
    ])  # Land area in square feet

    # Quantities of materials required (based on land area)
    y_gravel = np.array([25, 50, 75, 100, 125, 150, 175, 200, 225, 250])
    y_insulation_material = np.array([20, 40, 60, 80, 100, 120, 140, 160, 180, 200])
    y_adhesive = np.array([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    y_concrete_blocks = np.array([1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000])
    y_electrical_wire = np.array([50, 100, 150, 200, 250, 300, 350, 400, 450, 500])
    y_pipes = np.array([25, 50, 75, 100, 125, 150, 175, 200, 225, 250])
    y_paint = np.array([5, 10, 15, 20, 25, 30, 35, 40, 45, 50])
    y_tiles = np.array([250, 500, 750, 1000, 1250, 1500, 1750, 2000, 2250, 2500])
    y_wood = np.array([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    y_steel = np.array([500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000])
    y_bricks = np.array([5000, 10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000])
    y_sand = np.array([100, 200, 300, 400, 500, 600, 700, 800, 900, 1000])
    y_cement = np.array([20, 40, 60, 80, 100, 120, 140, 160, 180, 200])

    # Train models for each material
    model_gravel = TheilSenRegressor().fit(X, y_gravel)
    model_insulation_material = TheilSenRegressor().fit(X, y_insulation_material)
    model_adhesive = TheilSenRegressor().fit(X, y_adhesive)
    model_concrete_blocks = TheilSenRegressor().fit(X, y_concrete_blocks)
    model_wiring = TheilSenRegressor().fit(X, y_electrical_wire)
    model_pipes = TheilSenRegressor().fit(X, y_pipes)
    model_paint = TheilSenRegressor().fit(X, y_paint)
    model_tiles = TheilSenRegressor().fit(X, y_tiles)
    model_wood = TheilSenRegressor().fit(X, y_wood)
    model_steel = TheilSenRegressor().fit(X, y_steel)
    model_bricks = TheilSenRegressor().fit(X, y_bricks)
    model_sand = TheilSenRegressor().fit(X, y_sand)
    model_cement = TheilSenRegressor().fit(X, y_cement)

    return {
        'gravel':model_gravel,
        'insulation_material': model_insulation_material,
        'adhesive': model_adhesive,
        'concrete_blocks': model_concrete_blocks,
        'electrical_wire': model_wiring,
        'pipes': model_pipes,
        'paint': model_paint,
        'tiles': model_tiles,
        'wood': model_wood,
        'steel': model_steel,
        'bricks': model_bricks,
        'sand': model_sand,
        'cement': model_cement
    }


# Load trained models (in practice, load from a file or database)
models = train_theilsen_model()

#units = {'kilogram','cubic meter',' brick','cubic feet','square foot','cubic feet','kilogram','square foot','brick','meter',
#         'liter','meter','kilogram'}

def estimate_materials(request,construction_id):
        datas=ConstructionData.objects.get(id=construction_id)
        customer=datas.Customer
        land_area=datas.land_area
        Materials_expectations=datas.materials_expectations
        # Predict quantities of materials required
        predictions = {
            'insulation_material': models['insulation_material'].predict([[land_area]])[0],
            'adhesive': models['adhesive'].predict([[land_area]])[0],
            'concrete_blocks': models['concrete_blocks'].predict([[land_area]])[0],
            'electrical_wire': models['electrical_wire'].predict([[land_area]])[0],
            'pipes': models['pipes'].predict([[land_area]])[0],
            'paint': models['paint'].predict([[land_area]])[0],
            'tiles': models['tiles'].predict([[land_area]])[0],
            'wood': models['wood'].predict([[land_area]])[0],
            'steel': models['steel'].predict([[land_area]])[0],
            'bricks': models['bricks'].predict([[land_area]])[0],
            'sand': models['sand'].predict([[land_area]])[0],
            'cement': models['cement'].predict([[land_area]])[0],
            'gravel': models['gravel'].predict([[land_area]]) [0]
        }


        if Materials_expectations == 'High-quality':
            cost_dict = {material.material_name: material.cost_per_unit for material in
                         High_quality_materialCost.objects.all()}
            quality='High-quality'
        elif Materials_expectations == 'High-quality':
            cost_dict = {material.material_name: material.cost_per_unit for material in
                         Standard_quality_materialCost.objects.all()}
            quality = 'Standard-quality'
        else:
            cost_dict = {material.material_name: material.cost_per_unit for material in
                         Medium_quality_materialCost.objects.all()}
            quality='Medium-quality'


        material_unit={material.material_name:material.units for material in High_quality_materialCost.objects.all()}


        # Calculate cost and quantity for each material
        cost_breakdown = {}
        material_quantity = {}
        materials_info={}
        for material, quantity in predictions.items():
                materials_units = material_unit.get(material,0)
                unit_cost = cost_dict.get(material, 0)  # Default to 0 if not found
                cost_breakdown[material] = round(quantity * unit_cost)
                material_quantity[material] = round(quantity)

                materials_info[material]=[round(quantity),materials_units,round(quantity * unit_cost),quality]


        total_cost = sum(cost_breakdown.values())

        # Save the estimated quantities and total cost in the ConstructionData model
        datas.material_quantities = material_quantity
        datas.total_cost = total_cost
        datas.save()

        context = {
                'total_cost': total_cost,
                'material_and_cost_estimation': materials_info,
                'material_data': datas,
                'land_area': land_area,
                'customer':customer
            }
        return render(request, 'theil-sen_result.html', {'data': context})


#Message
def manager_to_customer_msg(request):
    if request.method=='POST':
        manager_id=request.session.get('manager_id')
        try:
            Sender=Project_manager.objects.get(id=manager_id)
        except Project_manager.DoesNotExist:
            messages.error(request, 'Manager not exists...')

        receiver = request.POST.get('to')
        try:
            Receiver = customer_details.objects.get(Name=receiver)
        except customer_details.DoesNotExist:
            messages.error(request, 'Customer not exists...')
            return redirect('manager_to_customer_msg')

        Subject = request.POST.get('subject')
        #if Subject is not None:
        File = request.FILES.get('report')
        Description = request.POST.get('message')
        sender_content_type = ContentType.objects.get_for_model(Project_manager)
        receiver_content_type = ContentType.objects.get_for_model(customer_details)


        if Subject == 'Other':
            custom_subject = request.POST.get('custom_subject')
            db = Message.objects.create(
                sender_content_type=sender_content_type,
                sender_object_id=Sender.id,
                receiver_content_type=receiver_content_type,
                receiver_object_id=Receiver.id,
                subject=custom_subject,
                file=File,
                description=Description
            )
            db.save()
        else:
            db = Message.objects.create(
                sender_content_type=sender_content_type,
                sender_object_id=Sender.id,
                receiver_content_type=receiver_content_type,
                receiver_object_id=Receiver.id,
                subject=Subject,
                file=File,
                description=Description
            )
            db.save()

        messages.success(request, 'Message sent....')
        return redirect('manager_to_customer_msg')

    return render(request,'manager_to_customer_msg.html')
def manager_to_customer_report(request):
    if request.method=='POST':
        manager_id=request.session.get('manager_id')
        try:
          Sender=Project_manager.objects.get(id=manager_id)
        except Project_manager.DoesNotExist:
            messages.error(request,'Manager Not Exist...')
            return redirect('manager_to_customer_report')

        receiver=request.POST.get('to')
        try:
            Receiver = customer_details.objects.get(Name=receiver)
        except customer_details.DoesNotExist:
            messages.error(request,'Customer not exists...')
            return redirect('manager_to_customer_report')

        Subject=request.POST.get('subject')
        File=request.FILES.get('report')
        Description=request.POST.get('message')

        sender_content_type=ContentType.objects.get_for_model(Project_manager)
        receiver_content_type=ContentType.objects.get_for_model(customer_details)

        db=Message.objects.create(
            sender_content_type=sender_content_type,
            sender_object_id=Sender.id,
            receiver_content_type=receiver_content_type,
            receiver_object_id=Receiver.id,
            subject=Subject,
            file=File,
            description=Description
        )
        db.save()
        project_db=project_details.objects.get(Customer=Receiver)
        project_db.Project_manager=Sender.Name
        project_db.cost_report=File
        project_db.Status='Customer project initiation form analysed and the report is sent to customer!'
        project_db.save()
        messages.success(request,'Report sent......!')
        return redirect('manager_to_customer_report')
    return render(request,'manager_to_customer_report.html')

#customer_response

def project_update_accepted(request):
    try:
        customer_id=request.session.get('customer_id')
        customer=customer_details.objects.get(id=customer_id)

        try:
             project=project_details.objects.get(Customer=customer)
             print("PROJECT:", project)
             if project.Customer_confirmation == None or project.Customer_confirmation == 'Customer Declined The Analysis Report':
                 project.Customer_confirmation='Customer Accepted The Updated Project Details'
                 project.Status='Customer Accepted The Updated Project Details'
                 project.Reason=None
                 project.save()
                 return render(request,'view_customer_message.html',{'resposne':project.Status})
             else:
                 data='You already responed..!'
                 return render(request, 'view_customer_message.html', {'already_respond': data})
        except  project_details.DoesNotExist:
            data='This project is deleted.'
            return render(request,'view_customer_message.html',{'DoesNotExist':data})
    except Exception as error:
        return HttpResponse('Nothing........')

def project_accepted(request):
    try:
        customer_id=request.session.get('customer_id')
        customer=customer_details.objects.get(id=customer_id)

        try:
             project=project_details.objects.get(Customer=customer)
             print("PROJECT:", project)
             if (project.Customer_confirmation == None or project.Customer_confirmation == 'Customer Declined The Analysis Report' or
                 project.Customer_confirmation=='Customer Accepted The Updated Project Details'):
                 project.Customer_confirmation='Customer Accepted The Analysis Report'
                 project.Status='Customer Accepted The Analysis Report'
                 project.Reason=None
                 project.save()
                 return render(request,'view_customer_message.html',{'resposne':project.Status})
             else:
                 data='You already responed..!'
                 return render(request, 'view_customer_message.html', {'already_respond': data})
        except  project_details.DoesNotExist:
            data='This project is deleted.'
            return render(request,'view_customer_message.html',{'DoesNotExist':data})
    except Exception as error:
        return HttpResponse('Nothing........')

def project_declined(request):
    try:
        customer_id=request.session.get('customer_id')
        customer=customer_details.objects.get(id=customer_id)

        try:
             project=project_details.objects.get(Customer=customer)
             print("PROJECT:", project)
             if ( project.Customer_confirmation == 'Customer Declined The Analysis Report' or project.Customer_confirmation == 'Customer Accepted The Analysis Report' or
                  project.Customer_confirmation=='Customer Accepted The Updated Project Details'):
                 data = 'You already responed..!'
                 return render(request, 'view_customer_message.html', {'already_respond': data})
             else:
                 return render(request, 'declined_reason.html', {'noresponse': 'None'})

        except  project_details.DoesNotExist:
            data='This project is deleted.'
            return render(request,'view_customer_message.html',{'DoesNotExist':data})
    except Exception as error:
        return HttpResponse('Nothing........')


def submit_decline_reason(request):
    if request.method=='POST':
        reason=request.POST.get('reason')
        customer_id=request.session.get('customer_id')
        customer=customer_details.objects.get(id=customer_id)
        project=project_details.objects.get(Customer=customer)
        project.Customer_confirmation='Customer Declined The Analysis Report'
        project.Status='Customer Declined The Analysis Report'
        project.Reason=reason
        project.save()
        response=project.Status
        return render(request,'declined_reason.html',{'response':response})
    return render(request,'declined_reason.html')

def customer_approve(request):
    try:
        projects = project_details.objects.all()
        projects_list=[]
        for project in projects:
          if project.cost_report is not None:
             if (project.Status == 'Customer Accepted The Analysis Report' or project.Status == 'Customer Declined The Analysis Report' or
                project.Status == 'Customer project initiation form analysed and the report is sent to customer!' or
                project.Status == 'Project Details Updated and Sent for Customer Review' or project.Status == 'Customer Accepted The Updated Project Details'):
                projects_list.append(project)
        print("PROJECT_LIST:",projects_list)
        return render(request,'customer_accept.html',{'projects':projects_list})
    except Exception as error:
        return HttpResponse('Nothing...........!')

def accepted_project(request,project_id):
        try:

            project = project_details.objects.get(id=project_id)

            if project.Customer_confirmation == 'Customer Accepted The Analysis Report':
                return render(request, 'accepted_projects.html', {'project': project,'proceed_to_vendor':True})

            elif project.Customer_confirmation == 'Customer Accepted The Updated Project Details' and project.cost_report is None:
                data = 'Project accepted, but analysis is pending. Analyze the project before proceeding.'
                return render(request, 'accepted_projects.html', {'project': project, 'analyse_project': data})

            else:
                return render(request, 'accepted_projects.html')

        except project_details.DoesNotExist:

            return render(request, 'accepted_projects.html', {'error': 'Project not found.'})


def declined_projects(request,project_id):
    try:
        project = project_details.objects.get(id=project_id)
        if project is not None:
            return render(request,'declined_projects.html',{'project':project})
        else:
            return render(request, 'declined_projects.html')
    except Exception as error:
        #messages.success(request, 'No Declined Project...!')
        return render(request, 'declined_projects.html')

def message_vendor_report(request,project_id):
    return render(request,'manager_to_vendor_report.html',{'project_id':project_id})


def manager_to_vendor_msg(request):
    vendors=vendor_details.objects.all()
    if request.method=='POST':
        sender_id=request.session.get('manager_id')
        print('SENDER_ID:',sender_id)
        try:
            Sender=Project_manager.objects.get(id=sender_id)
        except Project_manager.DoesNotExist:
            messages.error(request,'Project Manager Not Exist...')
            return redirect('manager_to_vendor_msg')

        vendor=request.POST.get('vendor')
        try:
            Receiver=vendor_details.objects.get(Name=vendor)
        except vendor_details.DoesNotExist:
            messages.error(request,'Vendor Not Exist...')
            return redirect('manager_to_vendor_msg')

        Report=request.FILES.get('report')
        message=request.POST.get('message')
        Subject=request.POST.get('subject')
        sender_content_type=ContentType.objects.get_for_model(Project_manager)
        receiver_content_type=ContentType.objects.get_for_model(vendor_details)

        if Subject == 'Other':
            custom_subject = request.POST.get('custom_subject')
            db = Message.objects.create(
            sender_content_type=sender_content_type,
            sender_object_id=Sender.id,
            receiver_content_type=receiver_content_type,
            receiver_object_id=Receiver.id,
            file=Report,
            subject=custom_subject,
            description=message
            )
            db.save()
        else:
            db = Message.objects.create(
                sender_content_type=sender_content_type,
                sender_object_id=Sender.id,
                receiver_content_type=receiver_content_type,
                receiver_object_id=Receiver.id,
                file=Report,
                subject=Subject,
                description=message
            )
            db.save()
        messages.success(request,'Message sent.....!')
        return redirect('manager_to_vendor_msg')

    return render(request, 'manager_to_vendor_msg.html',{'vendors':vendors})

def manager_to_vendor_report_page(request,project_id):
    vendors = vendor_details.objects.all()
    return render(request,'manager_to_vendor_report.html',{'vendors':vendors,'project_id':project_id})

def manager_to_vendor_report(request,project_id):
    vendors=vendor_details.objects.all()
    if request.method=='POST':
        sender_id=request.session.get('manager_id')
        Sender=Project_manager.objects.get(id=sender_id)
        vendor=request.POST.get('vendor')
        try:
            Receiver=vendor_details.objects.get(Name=vendor)
        except vendor_details.DoesNotExist:
            messages.error(request,'Vendot Not Exist...')
            return redirect('manager_to_vendor_report_page',project_id=project_id)

        Report=request.FILES.get('report')
        message=request.POST.get('message')
        Subject=request.POST.get('subject')
        sender_content_type=ContentType.objects.get_for_model(Project_manager)
        receiver_content_type=ContentType.objects.get_for_model(vendor_details)

        db = Message.objects.create(
            sender_content_type=sender_content_type,
            sender_object_id=Sender.id,
            receiver_content_type=receiver_content_type,
            receiver_object_id=Receiver.id,
            file=Report,
            subject=Subject,
            description=message
            )
        db.save()
        try:
            project=project_details.objects.get(id=project_id)
            if project.vendor is None:
                        project.vendor = vendor
                        project.Status='Materials request has been successfully sent to the vendor for preparation from project manager.'
                        project.save()
                        messages.success(request, 'Request sent..!')
                        return redirect('manager_to_vendor_report_page',project_id=project_id)
            else:
                messages.success(request, 'Message sent..!')
                return redirect('manager_to_vendor_report_page',project_id=project_id)
        except Exception as error:
                messages.error(request,'Project Not Exist...')
                return redirect('manager_to_vendor_report_page',project_id=project_id)

    return render(request,'manager_to_vendor_report.html',{'vendors':vendors})

def send_materials_request(request,project_id):
    return redirect('message_vendor',project_id=project_id)



def vendor_message(request):
    vendor_id=request.session.get('vendor_id')
    vendor=vendor_details.objects.get(id=vendor_id)
    vendor_content_type=ContentType.objects.get_for_model(vendor_details)

    my_message=Message.objects.filter(receiver_content_type=vendor_content_type,
                                                          receiver_object_id=vendor.id).order_by('-timestamp')
    return render(request,'vendor_msg.html',{'messages':my_message})




#upload report to database
def upload_cost_report(request):
    return redirect('manager_to_customer_report')


def upload_materials_report(request):
    if request.method=='POST':
        customer_name=request.POST.get('to')
        report=request.FILES.get('materials_report')
        try:
            customer=customer_details.objects.get(Name=customer_name)
        except customer_details.DoesNotExist:
            messages.error(request,'Customer not exist...')
            return redirect('upload_materials_report')
        db=project_details.objects.get(Customer=customer)
        db.materials_report=report
        db.save()
        messages.success(request,'File uploaded!')
        return redirect('upload_materials_report')
    return render(request,'upload_materials_report.html')

#Delete_declined_project
def delete_declined_project(request,project_id):
    project=project_details.objects.get(id=project_id)
    project.delete()
    messages.error(request,'The project has been successfully deleted.')
    return redirect('declined_projects',project_id=0)

#no_response
def no_response(request,project_id):
    project=project_details.objects.get(id=project_id)
    return render(request,'no_response.html',{'project':project})


#vendor_signup

def vendor_signup(request):
    if request.method == 'POST':
        user_name = request.POST.get('Name')
        user_contact = request.POST.get('contact')
        user_email = request.POST.get('mail')
        user_password = request.POST.get('password')
        hash_password=make_password(user_password)
        db = vendor_details.objects.create(
            Name=user_name,
            Contact=user_contact,
            Email=user_email,
            Password=hash_password
        )
        db.save()
        return redirect('vendor_login')
    return render(request, 'vendor_signup.html')



def vendor_login(request):
    if request.method == 'POST':
        usermail = request.POST.get('email')
        password = request.POST.get('password')
        try:
            vendor = vendor_details.objects.get(Email=usermail)
            if check_password(password,vendor.Password):
                request.session['vendor_id'] = vendor.id  # Store vendor ID in session
                if vendor.is_approve == 'pending':
                    return redirect('vendor_pending')
                elif vendor.is_approve == 'declined':
                    return redirect('vendor_declined')
                else:
                    return redirect('vendor_interface')

            else:
                messages.error(request, 'Invalid Credentials')
                return redirect('vendor_login')

        except vendor_details.DoesNotExist:
            messages.error(request, 'Invalid Credentials')
            return redirect('vendor_login')
            #return HttpResponse('Not Exits......!')

    return render(request, 'vendor_login.html')

def vendor_pending(request):
    return render(request,'vendor_pending.html')

def vendor_declined(request):
    return render(request,'vendor_declined.html')
def vendor_interface(request):
    return render(request,'vendor_interface.html')

def vendor_home(request):
    return render(request,'vendor_home.html')
def Materials_requests(request):
    vendor_id=request.session.get('vendor_id')
    try:
        vendor=vendor_details.objects.get(id=vendor_id)
        requests=project_details.objects.filter(vendor=vendor.Name)
        projects_list=[]
        for data in requests:
            if (data.Status=='Materials request has been successfully sent to the vendor for preparation from project manager.'
               or data.Status=='Materials Report have been prepared and sent to the quality checker for inspection from project manager.'):
                  projects_list.append(data)
        return render(request,'Materials_requests.html',{'projects':projects_list})

    except ObjectDoesNotExist:
        return render(request,'Materials_requests.html')

def send_to_qc(request):
    return render(request,'send_to_qc.html')

#submit materials to qc

def submit_materials_to_qc(request):
    if request.method=='POST':
        vendor_id = request.session.get('vendor_id')
        vendor_instance = vendor_details.objects.get(id=vendor_id)
        Project_id=request.POST.get('project_id')
        cement_grade = request.POST.get('cement_grade')
        cement_qty = request.POST.get('Cement_quantity')
        sand_grade = request.POST.get('sand_grade')
        sand_qty = request.POST.get('sand_quantity')
        pipes_grade = request.POST.get('pipes_grade')
        pipes_qty = request.POST.get('pipes_quantity')
        steel_grade = request.POST.get('steel_grade')
        steel_qty = request.POST.get('steel_quantity')
        wood_grade = request.POST.get('wood_grade')
        wood_qty = request.POST.get('wood_quantity')
        concrete_block_grade = request.POST.get('concrete_blocks_grade')
        concrete_block_qty = request.POST.get('concrete_blocks_quantity')
        adhesive_grade = request.POST.get('adhesive_grade')
        adhesive_qty = request.POST.get('adhesive_quantity')
        insulation_grade = request.POST.get('insulation_grade')
        insulation_qty = request.POST.get('insulation_quantity')
        tiles_grade = request.POST.get('tiles_grade')
        tiles_qty = request.POST.get('tiles_quantity')
        bricks_grade = request.POST.get('bricks_grade')
        bricks_qty = request.POST.get('bricks_quantity')
        aggregate_grade = request.POST.get('aggregate_grade')
        aggregate_qty = request.POST.get('aggregate_quantity')
        wire_grade = request.POST.get('electrical_wire_grade')
        wire_qty = request.POST.get('electrical_wire_quantity')
        paint_grade = request.POST.get('paint_grade')
        paint_qty = request.POST.get('paint_quantity')
        gravel_grade = request.POST.get('gravel_grade')
        gravel_quantity = request.POST.get('gravel_quantity')

        materials = Materials_report_qc.objects.create(
            vendor=vendor_instance,
            project_id=int(Project_id),
            cement_grade=cement_grade,
            cement_quantity=cement_qty,
            sand_grade=sand_grade,
            sand_quantity=sand_qty,
            aggregate_grade=aggregate_grade,
            aggregate_quantity=aggregate_qty,
            steel_grade=steel_grade,
            steel_quantity=steel_qty,
            paint_grade=paint_grade,
            paint_quantity=paint_qty,
            bricks_grade=bricks_grade,
            bricks_quantity=bricks_qty,
            tiles_grade=tiles_grade,
            tiles_quantity=tiles_qty,
            insulation_grade=insulation_grade,
            insulation_quantity=insulation_qty,
            adhesive_grade=adhesive_grade,
            adhesive_quantity=adhesive_qty,
            concrete_blocks_grade=concrete_block_grade,
            concrete_block_quantity=concrete_block_qty,
            electrical_wire_grade=wire_grade,
            electrical_wire_quantity=wire_qty,
            pipes_grade=pipes_grade,
            pipes_quantity=pipes_qty,
            wood_grade=wood_grade,
            wood_quantity=wood_qty,
            gravel_grade = gravel_grade,
            gravel_quantity = gravel_quantity)
        materials.save()
        project=project_details.objects.get(id=Project_id)
        project.Status='Materials have been prepared and sent to the quality checker for inspection from vendor.'
        project.supply_id=materials.id
        project.save()

        messages.success(request,'Materials submitted successfully...!')
        return render(request, 'send_to_qc.html')

    return render(request, 'send_to_qc.html')


#Quality_Checker:
def quality_checker_signup(request):
    if request.method=='POST':
        user_name=request.POST.get('Name')
        user_contact=request.POST.get('contact')
        user_email=request.POST.get('mail')
        user_password=request.POST.get('password')
        hash_password=make_password(user_password)
        db=Quality_checker.objects.create(
            Name=user_name,
            Contact=user_contact,
            Email=user_email,
            Password=hash_password
        )
        db.save()
        return redirect('quality_checker_login')
    return render(request,'quality_checker_signup.html')



def quality_checker_login(request):
    if request.method=='POST':
        usermail=request.POST.get('email')
        password=request.POST.get('password')
        try:
            quality_checker= Quality_checker.objects.get(Email=usermail)
            if check_password(password,quality_checker.Password):
                request.session['quality_checker_id'] = quality_checker.id  # Store quality_checker ID in session
                if quality_checker.is_approve == 'pending':
                    return redirect('quality_checker_pending')
                elif quality_checker.is_approve == 'declined':
                    return redirect('quality_checker_declined')
                else:
                    return redirect('quality_checker_interface')
            else:
                messages.error(request,'Invalid Credentials')
                return redirect('quality_checker_login')
        except Quality_checker.DoestNotExist:
            messages.error(request, 'Invalid Credentials')
            return redirect('quality_checker_login')

    return render(request,'quality_checker_login.html')

def quality_checker_pending(request):
    return render(request,'quality_checker_pending.html')
def quality_checker_declined(request):
    return render(request,'quality_checker_declined.html')
def quality_checker_interface(request):
    return render(request,'quality_checker_interface.html')

def quality_checker_home(request):
    return render(request,'quality_checker_home.html')
def manager_to_quality_checker_msg(request):
    quality_checker = Quality_checker.objects.all()
    if request.method=='POST':
        sender_id=request.session.get('manager_id')
        try:
            Sender=Project_manager.objects.get(id=sender_id)
        except Project_manager.DoesNotExist:
            messages.error(request,'Project Manager Not Exist...')
            return redirect('manager_to_quality_checker_msg')

        quality_checker=request.POST.get('quality_checker')
        try:
            Receiver=Quality_checker.objects.get(Name=quality_checker)
        except Quality_checker.ObjectDoesNotExist:
            messages.error(request, 'Quality_checker not exists.....')
            return redirect('manager_to_quality_checker_msg')

        Report=request.FILES.get('report')
        message=request.POST.get('message')
        Subject=request.POST.get('subject')
        manager_content_type=ContentType.objects.get_for_model(Project_manager)
        receiver_content_type=ContentType.objects.get_for_model(Quality_checker)

        if Subject == 'Other':
            custom_subject=request.POST.get('custom_subject')
            db=Message.objects.create(
            sender_content_type=manager_content_type,
            sender_object_id=Sender.id,
            receiver_content_type=receiver_content_type,
            receiver_object_id=Receiver.id,
            file=Report,
            subject=custom_subject,
            description=message
            )
            db.save()
        else:
            db = Message.objects.create(
                sender_content_type=manager_content_type,
                sender_object_id=Sender.id,
                receiver_content_type=receiver_content_type,
                receiver_object_id=Receiver.id,
                file=Report,
                subject=Subject,
                description=message
            )
            db.save()
        messages.success(request,'Message sent.....!')
        return redirect('manager_to_quality_checker_msg')

    return render(request,'manager_to_quality_checker_msg.html',{'quality_checkers':quality_checker})

def manager_to_quality_checker_report_page(request,project_id):
    quality_checker = Quality_checker.objects.all()
    return render(request,'manager_to_quality_checker_report.html',{'quality_checkers':quality_checker,'project_id':project_id})


def manager_to_quality_checker_report(request,project_id):
    quality_checker = Quality_checker.objects.all()
    if request.method=='POST':
        sender_id=request.session.get('manager_id')
        Sender=Project_manager.objects.get(id=sender_id)
        quality_checker=request.POST.get('quality_checker')
        try:
            Receiver=Quality_checker.objects.get(Name=quality_checker)
        except Quality_checker.DoesNotExist:
            messages.error(request,'Quality Chcekr Not Exist...')
            return redirect('manager_to_quality_checker_report_page',project_id=project_id)

        Report=request.FILES.get('report')
        message=request.POST.get('message')
        Subject=request.POST.get('subject')
        manager_content_type=ContentType.objects.get_for_model(Project_manager)
        receiver_content_type=ContentType.objects.get_for_model(Quality_checker)
        db=Message.objects.create(
        sender_content_type=manager_content_type,
        sender_object_id=Sender.id,
        receiver_content_type=receiver_content_type,
        receiver_object_id=Receiver.id,
        file=Report,
        subject=Subject,
        description=message
        )
        db.save()
        try:
        # project_id=request.session.get('project_id')
        #print("PROJECT_ID:",project_id)
           project=project_details.objects.get(id=project_id)
        except project_details.DoesNotExist:
            messages.error(request,'Project Not Exist...')
            return redirect('manager_to_quality_checker_report_page',project_id=project_id)

        project.quality_checker = quality_checker
        project.Status='Materials Report have been prepared and sent to the quality checker for inspection from project manager.'
        project.save()
        messages.success(request, 'Report sent.......!')
        return redirect('manager_to_quality_checker_report_page',project_id=project_id)

        #return redirect('manager_to_quality_checker_report', project_id=project_id)

    return render(request,'manager_to_quality_checker_report.html',{'quality_checkers':quality_checker,'project_id':project_id})


#qc_result
def quality_check_update(request):
        projects = project_details.objects.all()
        project_list=[]
        for project in projects:
            if (project.Status =='Quality Check report has been sent to the Project Manager.' or
               project.Status =='Materials Report have been prepared and sent to the quality checker for inspection from project manager.' or
               project.Status == 'Materials have been prepared and sent to the quality checker for inspection from vendor.' or
               project.Status == 'Re-Prepare Failed Materials'):

               project_list.append(project)
        return render(request, 'quality_check_update.html', {'projects': project_list})



def manager_qc_report(request):
    quality_checker_id=request.session.get('quality_checker_id')
    try:
        quality_checker=Quality_checker.objects.get(id=quality_checker_id)
        if quality_checker is not None:
            try:
                 projects=project_details.objects.filter(quality_checker=quality_checker.Name)
                 if projects is not None:
                     project_list=[]
                     for project in projects:
                        if project.Status=='Materials have been prepared and sent to the quality checker for inspection from vendor.':
                            project_list.append(project)
                     return render(request,'manager_report_qc.html',{'projects':project_list})
            except ObjectDoesNotExist:
                return HttpResponse('No projects.......!')
    except ObjectDoesNotExist:
        return HttpResponse('Quality_checker not exists.....')

    return render(request,'manager_report_qc.html')

#evaluate_materials

def evaluate_materials(request,project_id):
    project=project_details.objects.get(id=project_id)
    get_supply_id=project.supply_id
    get_quality=project.Materials
    get_land_area=project.Land_area


    return render(request,'evaluate_materials.html',{'supply_id':get_supply_id,'quality':get_quality,
                                                     'land_area':get_land_area})

def analyze_material_report(request):
    if request.method == 'POST':
        supply_id = request.POST.get('supply_id')
        Quality_check = request.POST.get('quality')
        Land_area = request.POST.get('land_area')
        land_area = float(Land_area)
        report = Materials_report_qc.objects.get(id=supply_id)

        def evaluate_quality(grade):
            quality_mapping = {
                'A': 'High-quality',
                'B+': 'Standard-quality',
                'B': 'Medium-quality',
            }
            return quality_mapping.get(grade, 'Low Quality')

            # Quantity analysis
        def analyze_quantity(land_area):
                # Your prediction logic for each material
                predictions = {
                    'insulation_material': models['insulation_material'].predict([[land_area]])[0],
                    'adhesive': models['adhesive'].predict([[land_area]])[0],
                    'concrete_blocks': models['concrete_blocks'].predict([[land_area]])[0],
                    'wire': models['electrical_wire'].predict([[land_area]])[0],
                    'pipes': models['pipes'].predict([[land_area]])[0],
                    'paint': models['paint'].predict([[land_area]])[0],
                    'tiles': models['tiles'].predict([[land_area]])[0],
                    'wood': models['wood'].predict([[land_area]])[0],
                    'steel': models['steel'].predict([[land_area]])[0],
                    'bricks': models['bricks'].predict([[land_area]])[0],
                    'sand': models['sand'].predict([[land_area]])[0],
                    'cement': models['cement'].predict([[land_area]])[0],
                    'gravel': models['gravel'].predict([[land_area]])[0]
                }

                material_sufficiency_checks = {
                    'concrete_blocks': float(report.concrete_block_quantity) >= round(predictions['concrete_blocks']),
                    'cement': float(report.cement_quantity) >= round(predictions['cement']),
                    'sand': float(report.sand_quantity) >= round(predictions['sand']),
                    'paint': float(report.paint_quantity) >= round(predictions['paint']),
                    'pipes': float(report.pipes_quantity) >= round(predictions['pipes']),
                    'adhesive': float(report.adhesive_quantity) >= round(predictions['adhesive']),
                    'bricks': float(report.bricks_quantity) >= round(predictions['bricks']),
                    'insulation_material': float(report.insulation_quantity) >= round(predictions['insulation_material']),
                    'wire': float(report.electrical_wire_quantity) >= round(predictions['wire']),
                    'wood': float(report.wood_quantity) >= round(predictions['wood']),
                    'tiles': float(report.tiles_quantity) >= round(predictions['tiles']),
                    'steel': float(report.steel_quantity) >= round(predictions['steel']),
                    'gravel': float(report.gravel_quantity) >= round(predictions['gravel']),
                }

                # Collect materials with insufficient quantities
                insufficient_materials = [material for material, sufficient in material_sufficiency_checks.items() if
                                          not sufficient]

                return insufficient_materials if insufficient_materials else []

        # Quality analysis
        def analyze_quality(Quality_check):
                quality_checks = {
                    'cement': report.cement_grade,
                    'sand': report.sand_grade,
                    'aggregate': report.aggregate_grade,
                    'steel': report.steel_grade,
                    'paint': report.paint_grade,
                    'bricks': report.bricks_grade,
                    'tiles': report.tiles_grade,
                    'insulation_material': report.insulation_grade,
                    'adhesive': report.adhesive_grade,
                    'concrete_blocks': report.concrete_blocks_grade,
                    'wire': report.electrical_wire_grade,
                    'pipes': report.pipes_grade,
                    'wood': report.wood_grade,
                    'gravel': report.gravel_grade,
                }

                # Collect materials with mismatched quality
                mismatched_materials = [material for material, grade in quality_checks.items() if
                                        evaluate_quality(grade) != Quality_check]

                return mismatched_materials if mismatched_materials else []

            # Perform the analyses
        insufficient_materials = analyze_quantity(land_area)
        mismatched_materials = analyze_quality(Quality_check)

        analysis = QualityAnalysis.objects.create(
            material_report=report,
            cement_quality=evaluate_quality(report.cement_grade),
            sand_quality=evaluate_quality(report.sand_grade),
            aggregate_quality=evaluate_quality(report.aggregate_grade),
            steel_quality=evaluate_quality(report.steel_grade),
            paint_quality=evaluate_quality(report.paint_grade),
            bricks_quality=evaluate_quality(report.bricks_grade),
            tiles_quality=evaluate_quality(report.tiles_grade),
            insulation_quality=evaluate_quality(report.insulation_grade),
            adhesive_quality=evaluate_quality(report.adhesive_grade),
            concrete_quality=evaluate_quality(report.concrete_blocks_grade),
            electrical_wire_quality=evaluate_quality(report.electrical_wire_grade),
            pipes_quality=evaluate_quality(report.pipes_grade),
            wood_quality=evaluate_quality(report.wood_grade),
            gravel_quality=evaluate_quality(report.gravel_grade),
            sufficient_materials=insufficient_materials,
            materials_quality=mismatched_materials
        )
        analysis.save()
        project=project_details.objects.get(supply_id=supply_id)
        return render(request, 'quality_check_result.html', {'Result': analysis, 'project':project})
    return render(request,'evaluate_materials.html')




def quality_checker_to_manager_msg(request):
    manager=Project_manager.objects.all()
    if request.method == 'POST':
        quality_checker_id = request.session.get('quality_checker_id')
        try:
            Sender = Quality_checker.objects.get(id=quality_checker_id)
        except Quality_checker.DoesNotExist:
            messages.error(request,'Quality Checker Not Exist... ')
            return redirect('quality_checker_to_manager_msg')

        receiver = request.POST.get('manager')
        try:
             Receiver = Project_manager.objects.get(Name=receiver)
        except Project_manager.DoesNotExit:
            messages.error(request,'Manager not exists...')
            return redirect('quality_checker_to_manager_msg')

        Subject = request.POST.get('subject')
        File = request.FILES.get('report')
        Description = request.POST.get('message')

        sender_type=ContentType.objects.get_for_model(Quality_checker)
        receiver_type=ContentType.objects.get_for_model(Project_manager)
        db = Message.objects.create(
            sender_content_type=sender_type,
            sender_object_id=Sender.id,
            receiver_content_type=receiver_type,
            receiver_object_id=Receiver.id,
            subject=Subject,
            file=File,
            description=Description
        )
        db.save()
        messages.success(request,'Message sent....!')
        return redirect('quality_checker_to_manager_msg')
    return render(request,'quality_checker_to_manager_msg.html',{'managers':manager})


def quality_checker_to_manager_report_page(request,project_id):
    managers = Project_manager.objects.all()
    return render(request, 'quality_checker_to_manager_report.html', {'managers': managers,'project_id':project_id})


def quality_checker_to_manager_report(request,project_id):
    manager=Project_manager.objects.all()
    if request.method == 'POST':
        quality_checker_id = request.session.get('quality_checker_id')
        try:
            Sender = Quality_checker.objects.get(id=quality_checker_id)
        except Quality_checker.DoesNotExist:
            messages.error(request,'Quality Checker Not Exist...')
            return redirect('quality_checker_to_manager_report_page', project_id=project_id)

        receiver = request.POST.get('manager')
        try:
             Receiver = Project_manager.objects.get(Name=receiver)
        except Project_manager.DoesNotExit:
            messages.error(request,'Manager not exists...')
            return redirect('quality_checker_to_manager_report_page',project_id=project_id)

        Subject = request.POST.get('subject')
        File = request.FILES.get('report')
        Description = request.POST.get('message')

        sender_type=ContentType.objects.get_for_model(Quality_checker)
        receiver_type=ContentType.objects.get_for_model(Project_manager)
        db = Message.objects.create(
            sender_content_type=sender_type,
            sender_object_id=Sender.id,
            receiver_content_type=receiver_type,
            receiver_object_id=Receiver.id,
            subject=Subject,
            file=File,
            description=Description
        )
        db.save()
        project_db = project_details.objects.get(id=project_id)
        project_db.quality_check_report = File
        project_db.Status='Quality Check report has been sent to the Project Manager.'
        project_db.save()
        messages.success(request, 'Report sent......!')
        return redirect('quality_checker_to_manager_report_page',project_id=project_id)

    return render(request, 'quality_checker_to_manager_report.html',{'managers':manager})


def quality_checker_to_vendor_msg(request):
    vendors=vendor_details.objects.all()
    if request.method == 'POST':
        quality_checker_id = request.session.get('quality_checker_id')
        try:
            Sender = Quality_checker.objects.get(id=quality_checker_id)
        except Quality_checker.DoestNotExist:
            messages.error(request,'Quality Checker Not Exist...')
            return redirect('quality_checker_to_vendor_msg')

        receiver = request.POST.get('vendor')
        try:
             Receiver = vendor_details.objects.get(Name=receiver)
        except vendor_details.DoesNotExist:
            messages.error(request,'Vendor not exists...')
            return redirect('quality_checker_to_vendor_msg')

        Subject = request.POST.get('subject')
        File = request.FILES.get('report')
        Description = request.POST.get('message')

        sender_type=ContentType.objects.get_for_model(Quality_checker)
        receiver_type=ContentType.objects.get_for_model(vendor_details)
        db = Message.objects.create(
            sender_content_type=sender_type,
            sender_object_id=Sender.id,
            receiver_content_type=receiver_type,
            receiver_object_id=Receiver.id,
            subject=Subject,
            file=File,
            description=Description
        )
        db.save()
        messages.success(request,'Message sent....!')
        return redirect('quality_checker_to_vendor_msg')
    return render(request,'quality_checker_to_vendor_msg.html',{'vendors':vendors})

def vendor_to_manager_msg(request):
    Manager = Project_manager.objects.all()
    if request.method == 'POST':
        sender_id = request.session.get('vendor_id')
        try:
            Sender = vendor_details.objects.get(id=sender_id)
        except vendor_details.DoesNotExist:
            messages.error(request,'Vendor Not Exist...')
            return redirect('vendor_to_manager_msg')

        manager = request.POST.get('manager')
        try:
            Receiver = Project_manager.objects.get(Name=manager)
        except ObjectDoesNotExist:
            messages.error(request, 'Manager not exists.....')
            return redirect('vendor_to_manager_msg')

        Report = request.FILES.get('report')
        message = request.POST.get('message')
        Subject = request.POST.get('subject')
        manager_content_type = ContentType.objects.get_for_model(vendor_details)
        receiver_content_type = ContentType.objects.get_for_model(Project_manager)
        db = Message.objects.create(
        sender_content_type=manager_content_type,
        sender_object_id=Sender.id,
        receiver_content_type=receiver_content_type,
        receiver_object_id=Receiver.id,
        file=Report,
        subject=Subject,
        description=message
        )
        db.save()
        messages.success(request, 'Message sent.....!')
        return redirect('vendor_to_manager_msg')

    return render(request, 'vendor_to_manager_msg.html', {'managers': Manager})

def vendor_to_quality_checker_msg(request):
    Quality_checkers = Quality_checker.objects.all()
    if request.method == 'POST':
        sender_id = request.session.get('vendor_id')
        try:
            Sender = vendor_details.objects.get(id=sender_id)
        except vendor_details.DoesNotExist:
            messages.error(request,'Vendor Not Exist...')
            return redirect('vendor_to_quality_checker_msg')

        quality_checker = request.POST.get('quality_checker')
        try:
            Receiver = Quality_checker.objects.get(Name=quality_checker)
        except ObjectDoesNotExist:
            messages.error(request, 'Quality_checker not exists.....')
            return redirect('vendor_to_quality_checker_msg')

        Report = request.FILES.get('report')
        message = request.POST.get('message')
        Subject = request.POST.get('subject')
        manager_content_type = ContentType.objects.get_for_model(vendor_details)
        receiver_content_type = ContentType.objects.get_for_model(Quality_checker)
        db = Message.objects.create(
        sender_content_type=manager_content_type,
        sender_object_id=Sender.id,
        receiver_content_type=receiver_content_type,
        receiver_object_id=Receiver.id,
        file=Report,
        subject=Subject,
        description=message
        )
        db.save()
        messages.success(request, 'Message sent.....!')
        return redirect('vendor_to_quality_checker_msg')

    return render(request, 'vendor_to_quality_checker_msg.html', {'quality_checkers': Quality_checkers})


##################
def quality_checker_msg(request):
    quality_id=request.session.get('quality_checker_id')
    quality_checker=vendor_details.objects.get(id=quality_id)
    quality_checker_content_type=ContentType.objects.get_for_model(Quality_checker)

    my_message=Message.objects.filter(receiver_content_type=quality_checker_content_type,
                                                          receiver_object_id=quality_checker.id).order_by('-timestamp')
    return render(request,'quality_checker_msg.html',{'messages':my_message})

def view_message(request,message_id):
    message=Message.objects.get(id=message_id)
    return render(request,'view_message.html',{'message':message})


def notify_to_deliver(request):
    if request.method=='POST':
        project_id=request.POST.get('project_id')
        try:
            project=project_details.objects.get(id=project_id)
        except project_details.DoesNotExist:
            messages.error(request, 'Peoject Not Exist...')
            return redirect('notify_to_deliver')

        project.Status='Material Delivery Request Sent To Vendor.'
        project.save()
        messages.success(request,'Message sent...')
        return redirect('notify_to_deliver')
    return render(request,'notify_to_deliver.html')

def Reprepare_materials(request):
    if request.method=='POST':
        project_id=request.POST.get('project_id')
        report=request.FILES.get('report')
        try:
            project=project_details.objects.get(id=project_id)
            project.file=report
            project.Status='Re-Prepare Failed Materials'
            project.save()
            messages.success(request,'Message sent...')
            return redirect('Reprepare_materials')
        except project_details.DoesNotExist:
            messages.error(request,'Project not exist...')
            return redirect('Reprepare_materials')

    return render(request,'reprepare_materials.html')

def quality_approval_update(request):
    projects=project_details.objects.all()
    project_list=[]
    for project in projects:
            if (project.Status == 'Material Delivery Request Sent To Vendor.' or project.Status == 'Re-Prepare Failed Materials' or
                project.Status == 'Quality Check report has been sent to the Project Manager.' or
                project.Status == 'Materials have been prepared and sent to the quality checker for inspection from vendor.'):
                project_list.append(project)
    return render(request,'quality_approval_update.html',{'projects':project_list})

    #return render(request,'quality_approval_update.html')

def deliver_materials(request):
    if request.method=='POST':
        project_id=request.POST.get('project_id')
        try:
            project=project_details.objects.get(id=project_id)
            return render(request,'deliver_materials.html',{'details':project})
        except project_details.DoesNotExist:
            messages.error(request,'Project not exist...')

    return render(request,'deliver_materials.html')

def vendor_reprepare_materials(request):
    projects=project_details.objects.all()
    project_list=[]
    for project in projects:
            if project.Status=='Re-Prepare Failed Materials':
                project_list.append(project)
    return render(request,'vendor_reprepare_materials.html',{'projects':project_list})


def confirm_delivery(request,project_id):
    project=project_details.objects.get(id=project_id)
    project.Status="Materials have been successfully shipped to the Customer address for delivery."
    project.save()
    msg='Thank you!'
    return render(request,'deliver_materials.html',{'data':project,'message':msg})

def ongoing_projects_manager(request):
    projects=project_details.objects.all()
    project_list=[]
    for project in projects:
            status=['Project Initiation Form Submitted' ,'Project Manager Assigned', 'Customer Accepted The Analysis Report','Customer Declined The Analysis Report',
                    'Quality Check report has been sent to the Project Manager.',
                    'Re-Prepare Failed Materials','Materials have been prepared and sent to the quality checker for inspection from vendor.',
                    'Materials Report have been prepared and sent to the quality checker for inspection from project manager.',
                    'Materials request has been successfully sent to the vendor for preparation from project manager.',
                    'Project Completed', 'Work Finished', 'Fully Completed', 'Project Done', 'Finalized', 'Closed',
                    'Wrapped Up', 'Construction Completed', 'Work Completed','Project Completion Confirmed',
                    'Completed All Tasks', 'Ready for Handover', 'Project Closed',
                    'Customer project initiation form analysed and the report is sent to customer!',
                    ]

            if project.Status and project.Status.lower() not in [ s.lower() for s in status]:
                project_list.append(project)
    return render(request,'ongoing_projects_manager.html',{'projects':project_list})

    #return render(request,'ongoing_projects.html')

def get_update_id(request,project_id):
    return render(request,'update_status.html',{'project_id':project_id})
def update_status(request,project_id):
    if request.method=='POST':
        project=project_details.objects.get(id=project_id)
        get_status=request.POST.get('status')
        project.Status=get_status.lower()
        project.save()
        messages.success(request,'Status Updataed...!')

        return redirect('get_update_id',project_id=project_id)

    return render(request,'update_status.html')


#confirm_project_complete
def confirm_project_completion(request,project_id):
    project=project_details.objects.get(id=project_id)
    project.Status='Project Completion Confirmed'
    project.save()
    msg='Thank you!'
    return render(request,'view_my_projects.html',{'message':msg})

#Login & Log_out

# Logout view
def logout_customer(request):
    # Clear session
    request.session.flush()
    return redirect('home')

def logout_manager(request):
    # Clear session
    request.session.flush()
    return redirect('home')

def logout_vendor(request):
    # Clear session
    request.session.flush()
    return redirect('home')

def logout_quality_checker(request):
    # Clear session
    request.session.flush()
    return redirect('home')

def logout_admin(request):
    request.session.flush()
    return redirect('home')
def view_manager_request(request):
    try:
        project_managers=Project_manager.objects.filter(is_approve='pending')
        if project_managers:
              return render(request, 'view_manager_request.html',{'project_managers':project_managers})
    except Exception as error:
        return render(request,'view_manager_request.html')
    return render(request, 'view_manager_request.html')

def approve_manager(request,manager_id):
    manager=Project_manager.objects.get(id=manager_id)
    manager.is_approve='approved'
    manager.save()
    return redirect('view_manager_request')

def decline_manager(request,manager_id):
    manager=Project_manager.objects.get(id=manager_id)
    manager.is_approve='declined'
    manager.save()
    return redirect('view_manager_request')

def view_vendor_request(request):
    try:
        vendors=vendor_details.objects.filter(is_approve='pending')
        if vendors:
              return render(request, 'view_vendor_request.html',{'vendors':vendors})
    except Exception as error:
        return render(request,'view_vendor_request.html')

    return render(request, 'view_vendor_request.html')

def approve_vendor(request,vendor_id):
    vendor=vendor_details.objects.get(id=vendor_id)
    vendor.is_approve='approved'
    vendor.save()
    return redirect('view_vendor_request')

def decline_vendor(request,vendor_id):
    vendor=vendor_details.objects.get(id=vendor_id)
    vendor.is_approve='declined'
    vendor.save()
    return redirect('view_vendor_request')


def view_quality_checker_request(request):
    try:
        quality_checkers = Quality_checker.objects.filter(is_approve='pending')
        if quality_checkers:
            return render(request, 'view_quality_checker_request.html', {'quality_checkers': quality_checkers})
    except Exception as error:
        return render(request, 'view_quality_checker_request.html')

    return render(request, 'view_quality_checker_request.html')

def approve_quality_checker(request,quality_checker_id):
    quality_checker=Quality_checker.objects.get(id=quality_checker_id)
    quality_checker.is_approve='approve'
    quality_checker.save()
    return redirect('view_quality_checker_request')

def decline_quality_checker(request,quality_checker_id):
    quality_checker=Quality_checker.objects.get(id=quality_checker_id)
    quality_checker.is_approve='declined'
    quality_checker.save()
    return redirect('view_quality_checker_request')

#project_assignment

def view_new_projects_admin(request):
    try:
        projects=project_details.objects.filter(Status='Project Initiation Form Submitted')
        if projects:
            return render(request,'view_new_projects_admin.html',{'projects':projects})
    except Exception as error:
        return render(request, 'view_new_projects_admin.html')

    return render(request,'view_new_projects_admin.html')

def assign_project(request):
    project_managers=Project_manager.objects.all()
    if project_managers:
        return render(request, 'assign_project.html',{'project_managers':project_managers})
    return render(request,'assign_project.html')

def asign_project_to_manager(request):
    if request.method=='POST':
        get_project_id=request.POST.get('project_id')
        get_manager=request.POST.get('Project_Manager')
        try:
            project=project_details.objects.get(id=get_project_id)
            project.Project_manager=get_manager
            project.Status='Project Manager Assigned'
            project.save()
            messages.success(request,'Project Manager Assigned!')
            return redirect('assign_project')
        except project_details.DoesNotExist:
            messages.error(request, 'Project Not Exist')
            return redirect('assign_project')

    return render(request,'assign_project.html')

def pending_projects(request):
    try:
        projects = project_details.objects.all()
        Project=[]
        for project in projects:
            #status=['Project Manager Assigned','You project initiation form analysed and the report is sent to your message!']
            if project.Status == 'Project Manager Assigned':
                reason='Project Analysis Pending By Project Manager'
                Project.append((project,reason))
            elif ( project.Status == 'You project initiation form analysed and the report is sent to your message!'
                   and project.Customer_confirmation == None):
                reason='Awaiting Customer Response To Analysis Report'
                Project.append((project,reason))
            print("PROJECTS:",Project)
            return render(request,'pending_projects.html',{'projects':Project})
    except Exception as error:
        print("ERROR:",error)

    return render(request,'pending_projects.html')

def ongoing_projects_admin(request):
    projects=project_details.objects.all()
    project_list=[]
    status = ['Project Initiation Form Submitted',
              'Customer Declined The Analysis Report',
              'Project Completed',
              'Project Completion Confirmed',
              'Project Manager Assigned' ,
              'Project Analysis Pending By Project Manager']
    for project in projects:
        if project.Status:
            cleaned_status = project.Status.replace('.', '').strip()
            if cleaned_status and  cleaned_status.lower() not in [ s.lower() for s in status]:
                project_list.append(project)
    print("PROJECTS:",project_list)
    return render(request,'ongoing_projects_admin.html',{'projects':project_list})

    #return render(request,'ongoing_projects_admin.html')

def completed_projects(request):
    projects=project_details.objects.filter(Status='Project Completion Confirmed')
    return render(request,'completed_projects.html',{'projects':projects})

def delete_completed_project(request,project_id):
    project=project_details.objects.get(id=project_id)
    project.delete()
    messages.success(request,'Project Deleted Successfully!')
    return redirect('completed_projects')

def admin_to_manager(request):
    manager=Project_manager.objects.all()
    if request.method == 'POST':
        try:
            Sender = Admin.objects.get(id=1)
        except Admin.DoesNotExist:
            messages.error(request,'Admin Not Exist... ')
            return redirect('admin_to_manager')

        receiver = request.POST.get('manager')
        try:
             Receiver = Project_manager.objects.get(Name=receiver)
        except Project_manager.DoesNotExit:
            messages.error(request,'Manager not exists...')
            return redirect('admin_to_manager')

        Subject = request.POST.get('subject')
        File = request.FILES.get('report')
        Description = request.POST.get('message')

        sender_type=ContentType.objects.get_for_model(Admin)
        receiver_type=ContentType.objects.get_for_model(Project_manager)
        db = Message.objects.create(
            sender_content_type=sender_type,
            sender_object_id=Sender.id,
            receiver_content_type=receiver_type,
            receiver_object_id=Receiver.id,
            subject=Subject,
            file=File,
            description=Description
        )
        db.save()
        messages.success(request,'Message sent....!')
        return redirect('admin_to_manager')
    return render(request,'admin_to_manager.html',{'managers':manager})
def admin_to_vendor(request):
    vendors = vendor_details.objects.all()
    if request.method == 'POST':
        try:
            Sender = Admin.objects.get(id=1)
        except Admin.DoestNotExist:
            messages.error(request, 'Admin Not Exist...')
            return redirect('admin_to_vendor')

        receiver = request.POST.get('vendor')
        try:
            Receiver = vendor_details.objects.get(Name=receiver)
        except vendor_details.DoesNotExist:
            messages.error(request, 'Vendor not exists...')
            return redirect('admin_to_vendor')

        Subject = request.POST.get('subject')
        File = request.FILES.get('report')
        Description = request.POST.get('message')

        sender_type = ContentType.objects.get_for_model(Admin)
        receiver_type = ContentType.objects.get_for_model(vendor_details)
        db = Message.objects.create(
            sender_content_type=sender_type,
            sender_object_id=Sender.id,
            receiver_content_type=receiver_type,
            receiver_object_id=Receiver.id,
            subject=Subject,
            file=File,
            description=Description
        )
        db.save()
        messages.success(request, 'Message sent....!')
        return redirect('quality_checker_to_vendor_msg')
    return render(request, 'admin_to_vendor.html', {'vendors': vendors})

def admin_to_quality_checker(request):
    quality_checker = Quality_checker.objects.all()
    if request.method == 'POST':
        try:
            Sender = Admin.objects.get(id=1)
        except Admin.DoesNotExist:
            messages.error(request,'Admin Not Exist...')
            return redirect('admin_to_quality_checker')

        quality_checker = request.POST.get('quality_checker')
        try:
            Receiver = Quality_checker.objects.get(Name=quality_checker)
        except Quality_checker.DoesNotExist:
            messages.error(request, 'Quality Checker Not Exist...')
            return redirect('admin_to_quality_checker')

        Report = request.FILES.get('report')
        message = request.POST.get('message')
        Subject = request.POST.get('subject')
        admin_content_type = ContentType.objects.get_for_model(Admin)
        receiver_content_type = ContentType.objects.get_for_model(Quality_checker)
        db = Message.objects.create(
            sender_content_type=admin_content_type,
            sender_object_id=Sender.id,
            receiver_content_type=receiver_content_type,
            receiver_object_id=Receiver.id,
            file=Report,
            subject=Subject,
            description=message
        )
        db.save()
        messages.success(request, 'Message sent....!')
        return redirect('admin_to_quality_checker')

    return render(request, 'admin_to_quality_checker.html',{'quality_checkers': quality_checker})


def about(request):
    return render(request,'about.html')

def customer_about(request):
    return render(request,'customer_about.html')


def manager_about(request):
    return render(request,'manager_about.html')

def quality_checker_about(request):
    return render(request,'quality_checker_about.html')

def vendor_about(request):
    return render(request,'vendor_about.html')