"""
Open Real-world-based Annotation for Rare Diseases API
@author: Cong Liu

modified from

Columbia Open Health Data (COHD) API

implemented in Flask

@author: Joseph D. Romano
@author: Rami Vanguri
@author: Choonhan Youn
@author: Casey Ta
"""

from flask import request, redirect
from flask.templating import render_template

from .google_analytics import GoogleAnalytics

# Flask app and cache
from .app import app, cache

# app needs to be loaded before loading other COHD modules
from . import api_service
# from . import scheduled_tasks


##########
# ROUTES #
##########


@app.route('/')
def website():
    google_analytics(endpoint='/')
    # return "Hello World!"
    return render_template("index.html")


@app.route('/api')
@app.route('/api/')
def api_cohd():
    google_analytics(endpoint='/api')
    return redirect("https://smart-api.info/ui/aed21cd6828e18de3fa2da6a76574520", code=302)

@app.route('/api/metadata/datasets')
def api_meta_():
    google_analytics(service='metadata', meta='datasets')
    return api_call(service='metadata', meta='datasets')

@app.route('/api/metadata/domainCounts')
def api_meta_domain_counts():
    google_analytics(service='metadata', meta='domainCounts')
    return api_call(service='metadata', meta='domainCounts')

@app.route('/api/metadata/domainPairCounts')
def api_meta_domain_pair_counts():
    google_analytics(service='metadata', meta='domainPairCounts')
    return api_call(service='metadata', meta='domainPairCounts')

@app.route('/api/metadata/patientCounts')
def api_meta_patient_counts():
    google_analytics(service='metadata', meta='patientCount')
    return api_call(service='metadata', meta='patientCount')

@app.route('/api/vocabulary/findConceptByName')
def api_vocabulary_find_concept_by_name():
    google_analytics(service='vocabulary', meta='findConceptByName')
    return api_call(service='vocabulary', meta='findConceptByName')

@app.route('/api/vocabulary/findConceptById')
def api_vocabulary_find_concept_by_id():
    google_analytics(service='vocabulary', meta='findConceptById')
    return api_call(service='vocabulary', meta='findConceptById')

@app.route('/api/vocabulary/findConceptByCode')
def api_vocabulary_find_concept_by_code():
    google_analytics(service='vocabulary', meta='findConceptByCode')
    return api_call(service='vocabulary', meta='findConceptByCode')

@app.route('/api/vocabulary/findConceptByAny')
def api_vocabulary_find_concept_by_any():
    google_analytics(service='vocabulary', meta='findConceptByAny')
    return api_call(service='vocabulary', meta='findConceptByAny')

@app.route('/api/frequencies/singleConceptFreq')
def api_frequencies_single_concept_freq():
    google_analytics(service='frequencies', meta='singleConceptFreq')
    return api_call(service='frequencies', meta='singleConceptFreq')

@app.route('/api/frequencies/pairedConceptFreq')
def api_frequencies_paired_concept_freq():
    google_analytics(service='frequencies', meta='pairedConceptFreq')
    return api_call(service='frequencies', meta='pairedConceptFreq')   

@app.route('/api/frequencies/mostFrequency')
def api_frequencies_most_frequency():
    google_analytics(service='frequencies', meta='mostFrequency')
    return api_call(service='frequencies', meta='mostFrequency')   

@app.route('/api/association/chiSquare')
def api_association_chi_square():
    google_analytics(service='association', meta='chiSquare')
    return api_call(service='association', meta='chiSquare')   

@app.route('/api/association/obsExpRatio')
def api_association_obs_exp_ratio():
    google_analytics(service='association', meta='obsExpRatio')
    return api_call(service='association', meta='obsExpRatio')  

@app.route('/api/association/relativeFrequency')
def api_association_relative_frequency():
    google_analytics(service='association', meta='relativeFrequency')
    return api_call(service='association', meta='relativeFrequency')   

@app.route('/api/association/jaccardIndex')
def api_association_jaccard_index():
    google_analytics(service='association', meta='jaccardIndex')
    return api_call(service='association', meta='jaccardIndex')     

# Retrieves the desired arg_names from args and stores them in the queries dictionary. Returns None if any of arg_names
# are missing
def args_to_query(args, arg_names):
    query = {}
    for arg_name in arg_names:
        arg_value = args[arg_name]
        if arg_value is None or arg_value == ['']:
            return None
        query[arg_name] = arg_value
    return query


def google_analytics(endpoint=None, service=None, meta=None):
    # Report to Google Analytics iff the tracking ID is specified in the configuration file
    if 'GA_TID' in app.config:
        tid = app.config['GA_TID']
        GoogleAnalytics.google_analytics(request, tid, endpoint, service, meta)


@app.route('/api/query')
def api_call(service=None, meta=None, query=None, version=None):
    if service is None:
        service = request.args.get('service')
    if meta is None:
        meta = request.args.get('meta')

    print("Service: ", service)
    print("Meta/Method: ", meta)

    if service == [''] or service is None:
        result = 'No service selected', 400
    elif service == 'metadata':
        if meta.lower() == 'datasets':
            result = api_service.api_meta_datasets(request)
        elif meta.lower() == 'domaincounts':
            result = api_service.api_meta_domain_counts(request)
        elif meta.lower() == 'domainpaircounts':
            result = api_service.api_meta_domain_pair_counts(request)
        elif meta.lower() == 'patientcount':
            result = api_service.api_meta_paitient_counts(request)
        else:
            result = 'meta not recognized', 400
    elif service.lower() == 'vocabulary':
        if meta.lower() == 'findconceptbyname':
            result = api_service.api_vocabulary_find_concepts_by_name(request)
        elif meta.lower() == 'findconceptbyid':
            result = api_service.api_vocabulary_find_concepts_by_id(request)
        elif meta.lower() == 'findconceptbycode':
            result = api_service.api_vocabulary_find_concepts_by_code(request)
        elif meta.lower() == 'findconceptbyany':
            result = api_service.api_vocabulary_find_concepts_by_any(request)
        else:
            result = 'meta not recognized', 400
    elif service.lower() == 'frequencies':
        if meta.lower() == 'singleconceptfreq': 
            result = api_service.api_frequencies_single_concept_freq(request)
        elif meta.lower() == 'pairedconceptfreq':  
            result = api_service.api_frequencies_paired_concept_freq(request)
        elif meta.lower() == 'mostfrequency':  
            result = api_service.api_frequencies_most_frequency(request)
        else:
            result = 'meta not recognized', 400
    elif service.lower() == 'association':
        if meta.lower() == 'chisquare':
            result = api_service.api_association_chi_square(request)
        elif meta.lower() == 'obsexpratio':
            result = api_service.api_association_obs_exp_ratio(request)
        elif meta.lower() == 'relativefrequency':
            result = api_service.api_association_relative_frequency(request)
        elif meta.lower() == 'jaccardindex':
            result = api_service.api_association_jaccard_index(request)
        else:
            result = 'meta not recognized', 400
    else:
        result = 'service not recognized', 400

    # Report the API call to Google Analytics
    google_analytics(service=service, meta=meta)

    return result


if __name__ == "__main__":
    app.run()
    # app.run(host='localhost',debug=True)