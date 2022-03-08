import db_util as du 
from scipy.stats import chisquare
import pandas as pd 
import numpy as np

# Configuration
CONFIG_FILE = "database.cnf"  # log-in credentials for database
DATASET_ID_DEFAULT = 3
DOMAIN_ID_DEFAULT = 'phenotypes'
TOP_N_DEFAULT = 99999999
ASCENDING_DEFAULT = False
# DATASET_ID_DEFAULT_HIER = 3
# DEFAULT_CONFIDENCE = 0.99
# DEFAULT_HIERARCHICAL = 0



def api_meta_datasets(request):
    conn = du.sql_connection(CONFIG_FILE)
    cur = conn.cursor()
    json_return = {'results': du.get_datasets(cur=cur)}
    return json_return

def api_meta_domain_counts(request):
    dataset_id = get_arg_dataset_id(request.args)
    if dataset_id is None:
        return 'dataset_id parameter is missing or imcompatible', 400
    conn = du.sql_connection(CONFIG_FILE)
    cur = conn.cursor()
    results = du.get_domain_counts(cur=cur,dataset_id=dataset_id)
    json_return = {'results': results, 'parameter':{'dataset_id':dataset_id}}
    return json_return

def api_meta_domain_pair_counts(request):
    dataset_id = get_arg_dataset_id(request.args)
    if dataset_id is None:
        return 'dataset_id parameter is missing or imcompatible', 400
    conn = du.sql_connection(CONFIG_FILE)
    cur = conn.cursor()
    results = du.get_domain_pair_counts(cur=cur,dataset_id=dataset_id)        
    json_return = {'results': results, 'parameter':{'dataset_id':dataset_id}} # phenotype-disease and disease-phenotype will appear differently.
    return json_return

def api_meta_paitient_counts(request):
    dataset_id = get_arg_dataset_id(request.args)
    if dataset_id is None:
        return 'dataset_id parameter is missing or imcompatible', 400
    conn = du.sql_connection(CONFIG_FILE)
    cur = conn.cursor()
    results = du.get_total_patient_count(cur=cur,dataset_id=dataset_id)
    json_return = {'results': results, 'parameter':{'dataset_id':dataset_id}}
    return json_return

def api_vocabulary_find_concepts_by_name(request):
    domain_id = get_arg_domain_id(request.args)
    print(domain_id)
    q = get_arg_q(request.args,'q')
    if q == []:
        return 'q parameter is missing', 400
    conn = du.sql_connection(CONFIG_FILE)
    cur = conn.cursor()
    results = du.get_omop_id(cur=cur,concept_name_list=q,domain_id=domain_id)
    json_return = {'results': results, 'parameter':{'domain_id':domain_id, 'q': q}}
    return json_return

def api_vocabulary_find_concepts_by_id(request):
    q = get_arg_q(request.args,'q')
    if q == []:
        return 'q parameter is missing', 400
    conn = du.sql_connection(CONFIG_FILE)
    cur = conn.cursor()
    results = du.get_omop_id(cur=cur,concept_id_list=q)
    json_return = {'results': results, 'parameter':{'q': q}}
    return json_return

def api_vocabulary_find_concepts_by_code(request):
    q = get_arg_q(request.args,'q')
    if q == []:
        return 'q parameter is missing', 400
    conn = du.sql_connection(CONFIG_FILE)
    cur = conn.cursor()
    results = du.get_omop_id(cur=cur,concept_code_list=q)
    json_return = {'results': results, 'parameter':{'q': q}}
    return json_return

def api_vocabulary_find_concepts_by_any(request):
    domain_id = get_arg_domain_id(request.args)
    q = get_arg_q(request.args,'q')
    if q == []:
        return 'q parameter is missing', 400
    conn = du.sql_connection(CONFIG_FILE)
    cur = conn.cursor()
    results = du.get_omop_id(cur=cur,concept_id_list=q, concept_name_list=q, concept_code_list = q, domain_id=domain_id)
    json_return = {'results': results, 'parameter':{'domain_id':domain_id, 'q': q}}
    return json_return

def api_frequencies_single_concept_freq(request):
    dataset_id = get_arg_dataset_id(request.args)
    if dataset_id is None:
        return 'dataset_id parameter is missing or imcompatible', 400
    concept_id = get_arg_concept_id(request.args,'concept_id')
    if concept_id == []:
        return 'concept_id parameter is missing', 400
    conn = du.sql_connection(CONFIG_FILE)
    cur = conn.cursor()
    
    results = []
    patient_count = du.get_total_patient_count(cur=cur,dataset_id=dataset_id)
    if len(patient_count) == 1:
        single_count = pd.DataFrame(du.get_single_concept_count(cur=cur,dataset_id = dataset_id, concept_id_list=concept_id))
        if single_count.shape[0] > 0:
            concept_details = pd.DataFrame(du.get_omop_id(cur=cur,concept_id_list=concept_id))
            pts = float(patient_count[0]['count'])
            single_count['concept_frequency'] = single_count['concept_count'] / pts
            results = single_count.merge(concept_details).sort_values('concept_frequency',ascending=False)
            results = results.to_dict('records')
    json_return = {'results': results, 'parameter':{'dataset_id':dataset_id, 'concept_id': concept_id}}
    return json_return

def api_frequencies_paired_concept_freq(request):
    dataset_id = get_arg_dataset_id(request.args)
    if dataset_id is None:
        return 'dataset_id parameter is missing or imcompatible', 400
    concept_id_1 = get_arg_concept_id(request.args,'concept_id_1')
    if concept_id_1 == []:
        return 'concept_id_1 parameter is missing', 400
    concept_id_2 = get_arg_concept_id(request.args,'concept_id_2')
    if concept_id_2 == []:
        return 'concept_id_2 parameter is missing', 400
    conn = du.sql_connection(CONFIG_FILE)
    cur = conn.cursor()

    results = []
    patient_count = du.get_total_patient_count(cur=cur,dataset_id=dataset_id)
    if len(patient_count) == 1:
        pair_count = pd.DataFrame(du.get_pair_concept_count(cur=cur,dataset_id=dataset_id, concept_id_list_1=concept_id_1,concept_id_list_2=concept_id_2))
        if pair_count.shape[0] > 0:
            concept_details_1 = pd.DataFrame(du.get_omop_id(cur=cur,concept_id_list=concept_id_1))
            concept_details_1 = concept_details_1.rename(columns={'concept_id': 'concept_id_1','concept_name':'concept_name_1','concept_code':'concept_code_1','domain_id':'domain_id_1','vocabulary_id':'vocabulary_id_1'})
            concept_details_2 = pd.DataFrame(du.get_omop_id(cur=cur,concept_id_list=concept_id_2))
            concept_details_2 = concept_details_2.rename(columns={'concept_id': 'concept_id_2','concept_name':'concept_name_2','concept_code':'concept_code_2','domain_id':'domain_id_2','vocabulary_id':'vocabulary_id_2'})
            pts = float(patient_count[0]['count'])
            pair_count['concept_frequency'] = pair_count['concept_pair_count'] / pts
            results = pair_count.merge(concept_details_1).merge(concept_details_2).sort_values('concept_frequency',ascending=False)
            results = results.to_dict('records')

    json_return = {'results': results, 'parameter':{'dataset_id':dataset_id, 'concept_id_1': concept_id_1, 'concept_id_2': concept_id_2}}
    
    return json_return

def api_frequencies_most_frequency(request):
    dataset_id = get_arg_dataset_id(request.args)
    if dataset_id is None:
        return 'dataset_id parameter is missing or imcompatible', 400
    concept_id = get_arg_concept_id(request.args,'concept_id')
    if len(concept_id) > 1:
        return 'query multiple qs are not available', 400
    domain_id = get_arg_domain_id(request.args)
    top_n = get_arg_top_n(request.args)

    conn = du.sql_connection(CONFIG_FILE)
    cur = conn.cursor()
    results = []
    patient_count = du.get_total_patient_count(cur=cur,dataset_id=dataset_id)
    if len(patient_count) == 1:
        pts = float(patient_count[0]['count'])
        if len(concept_id) == 0:
            single_count = pd.DataFrame(du.get_single_concept_count(cur=cur,dataset_id = dataset_id,top_n=top_n,domain_id=domain_id))
            if single_count.shape[0] > 0:
                concept_list = list(set(single_count['concept_id'].tolist()))
                concept_details = pd.DataFrame(du.get_omop_id(cur=cur,concept_id_list=concept_list))
                pts = float(patient_count[0]['count'])
                single_count['concept_frequency'] = single_count['concept_count'] / pts
                results = single_count.merge(concept_details).sort_values('concept_frequency',ascending=False)
                results = results.to_dict('records')
        else:
            pair_count = pd.DataFrame(du.get_pair_concept_count(cur=cur,dataset_id=dataset_id, concept_id_list_1=concept_id, top_n = top_n, domain_id=domain_id))
            if pair_count.shape[0] > 0:
                concept_list_1 = list(set(pair_count['concept_id_1'].tolist()))
                concept_details_1 = pd.DataFrame(du.get_omop_id(cur=cur,concept_id_list=concept_list_1))
                concept_details_1 = concept_details_1.rename(columns={'concept_id': 'concept_id_1','concept_name':'concept_name_1','concept_code':'concept_code_1','domain_id':'domain_id_1','vocabulary_id':'vocabulary_id_1'})
                concept_list_2 = list(set(pair_count['concept_id_2'].tolist()))
                concept_details_2 = pd.DataFrame(du.get_omop_id(cur=cur,concept_id_list=concept_list_2))
                concept_details_2 = concept_details_2.rename(columns={'concept_id': 'concept_id_2','concept_name':'concept_name_2','concept_code':'concept_code_2','domain_id':'domain_id_2','vocabulary_id':'vocabulary_id_2'})
                pts = float(patient_count[0]['count'])
                pair_count['concept_frequency'] = pair_count['concept_pair_count'] / pts
                results = pair_count.merge(concept_details_1).merge(concept_details_2).sort_values('concept_frequency',ascending=False)
                results = results.to_dict('records')
    json_return = {'results': results, 'parameter':{'dataset_id':dataset_id, 'concept_id': concept_id, 'domain_id': domain_id, 'top_n': top_n}}
    return json_return

def api_association_jaccard_index(request):
    dataset_id = get_arg_dataset_id(request.args)
    if dataset_id is None:
        return 'dataset_id parameter is missing or imcompatible', 400
    concept_id_1 = get_arg_concept_id(request.args,'concept_id_1')
    if concept_id_1 == []:
        return 'concept_id_1 parameter is missing', 400
    concept_id_2 = get_arg_concept_id(request.args,'concept_id_2')
    domain_id = get_arg_domain_id(request.args)
    top_n = get_arg_top_n(request.args)
    ascending =get_arg_ascending(request.args)
    conn = du.sql_connection(CONFIG_FILE)
    cur = conn.cursor()

    results = []
    pair_count = pd.DataFrame(du.get_pair_concept_count(cur=cur,dataset_id=dataset_id,domain_id=domain_id, concept_id_list_1=concept_id_1,concept_id_list_2=concept_id_2))
    if pair_count.shape[0] > 0:
        # calculate jaccard_index.
        pair_count['jaccard_index'] = pair_count['concept_pair_count'] / (pair_count['concept_count_1'] + pair_count['concept_count_2'] - pair_count['concept_pair_count'])
        concept_list_1 = list(set(pair_count['concept_id_1'].tolist()))
        concept_details_1 = pd.DataFrame(du.get_omop_id(cur=cur,concept_id_list=concept_list_1))
        concept_details_1 = concept_details_1.rename(columns={'concept_id': 'concept_id_1','concept_name':'concept_name_1','concept_code':'concept_code_1','domain_id':'domain_id_1','vocabulary_id':'vocabulary_id_1'})
        
        # get weighted score.
        pair_count = _get_weighted_statistics(cur=cur,dataset_id=dataset_id,domain_id = domain_id,concept_id_1 = concept_list_1, pair_count_df = pair_count, json_key = 'jaccard_index')        
        high_level_summary = pair_count.groupby('concept_id_2')['jaccard_index'].agg('sum').reset_index()
        high_level_summary = high_level_summary.rename(columns={'jaccard_index': 'ws_jaccard_index'}).sort_values('ws_jaccard_index',ascending=ascending).head(top_n)
        concept_list_2 = list(set(high_level_summary['concept_id_2'].tolist()))
        concept_details_2 = pd.DataFrame(du.get_omop_id(cur=cur,concept_id_list=concept_list_2))
        concept_details_2 = concept_details_2.rename(columns={'concept_id': 'concept_id_2','concept_name':'concept_name_2','concept_code':'concept_code_2','domain_id':'domain_id_2','vocabulary_id':'vocabulary_id_2'})
        detailed_results = pair_count.merge(concept_details_1)
        results = high_level_summary.merge(detailed_results).groupby(['concept_id_2','ws_jaccard_index'])['concept_id_1','concept_name_1','concept_code_1','domain_id_1','vocabulary_id_1','concept_pair_count','w','jaccard_index'].apply(lambda x: x.to_dict('records')).reset_index(name='z_details')
        results = results.merge(concept_details_2).sort_values('ws_jaccard_index',ascending=ascending)
        results = results.to_dict('records')
    json_return = {'results': results, 'parameter':{'dataset_id':dataset_id, 'domain_id': domain_id, 'concept_id_1': concept_id_1, 'concept_id_2': concept_id_2, 'top_n': top_n, 'ascending': ascending}}
    return json_return

def api_association_chi_square(request):
    dataset_id = get_arg_dataset_id(request.args)
    if dataset_id is None:
        return 'dataset_id parameter is missing or imcompatible', 400
    concept_id_1 = get_arg_concept_id(request.args,'concept_id_1')
    if concept_id_1 == []:
        return 'concept_id_1 parameter is missing', 400
    concept_id_2 = get_arg_concept_id(request.args,'concept_id_2')
    domain_id = get_arg_domain_id(request.args)
    top_n = get_arg_top_n(request.args)
    ascending = get_arg_ascending(request.args)

    conn = du.sql_connection(CONFIG_FILE)
    cur = conn.cursor()

    results = []
    pair_count = pd.DataFrame(du.get_pair_concept_count(cur=cur,dataset_id=dataset_id,domain_id=domain_id, concept_id_list_1=concept_id_1,concept_id_list_2=concept_id_2))
    if pair_count.shape[0] > 0:
        # calculate chi-square.
        patient_count = du.get_total_patient_count(cur=cur,dataset_id=dataset_id)
        total_pair_count = du.get_total_pair_count(cur, dataset_id,domain_id=domain_id)
        pair_count['pts'] = float(patient_count[0]['count'])
        pair_count['pc'] = float(total_pair_count[0]['pair_count']) # used for p-value adj.
        pair_count['cpc'] = pair_count['concept_pair_count']
        pair_count['c1'] = pair_count['concept_count_1']
        pair_count['c2'] = pair_count['concept_count_2']
        pair_count['neg'] = pair_count['pts'] + pair_count['cpc'] - pair_count['c1'] - pair_count['c2']
        cs = pair_count.apply(lambda x: chisquare([x.neg, x.c1 - x.cpc, x.c2 - x.cpc, x.cpc], [(x.pts - x.c1) * (x.pts - x.c2) / x.pts, x.c1 * (x.pts - x.c2) / x.pts, x.c2 * (x.pts - x.c1) / x.pts, x.c1 * x.c2 / x.pts], 2), axis=1, result_type='expand')
        cs = cs.rename(columns={0:'cs',1:'pvalue'})
        pair_count['cs'] = cs['cs']
        pair_count['pvalue'] = cs['pvalue']
        print(pair_count)
        pair_count['adj_p'] = pair_count.apply(lambda x: min(x.pvalue * x.pc, 1.0),axis=1)


        concept_list_1 = list(set(pair_count['concept_id_1'].tolist()))
        concept_details_1 = pd.DataFrame(du.get_omop_id(cur=cur,concept_id_list=concept_list_1))
        concept_details_1 = concept_details_1.rename(columns={'concept_id': 'concept_id_1','concept_name':'concept_name_1','concept_code':'concept_code_1','domain_id':'domain_id_1','vocabulary_id':'vocabulary_id_1'})
        
        # get weighted score.
        pair_count = _get_weighted_statistics(cur=cur,dataset_id=dataset_id,domain_id = domain_id,concept_id_1 = concept_list_1, pair_count_df = pair_count, json_key = 'cs')        
        high_level_summary = pair_count.groupby('concept_id_2')['cs'].agg('sum').reset_index()
        high_level_summary = high_level_summary.rename(columns={'cs': 'ws_cs'}).sort_values('ws_cs',ascending=ascending).head(top_n)
        concept_list_2 = list(set(high_level_summary['concept_id_2'].tolist()))
        concept_details_2 = pd.DataFrame(du.get_omop_id(cur=cur,concept_id_list=concept_list_2))
        concept_details_2 = concept_details_2.rename(columns={'concept_id': 'concept_id_2','concept_name':'concept_name_2','concept_code':'concept_code_2','domain_id':'domain_id_2','vocabulary_id':'vocabulary_id_2'})
        detailed_results = pair_count.merge(concept_details_1)
        results = high_level_summary.merge(detailed_results).groupby(['concept_id_2','ws_cs'])['concept_id_1','concept_name_1','concept_code_1','domain_id_1','vocabulary_id_1','concept_pair_count','w','cs','pvalue','adj_p'].apply(lambda x: x.to_dict('records')).reset_index(name='z_details')
        results = results.merge(concept_details_2).sort_values('ws_cs',ascending=ascending)
        results = results.to_dict('records')
    json_return = {'results': results, 'parameter':{'dataset_id':dataset_id, 'domain_id': domain_id, 'concept_id_1': concept_id_1, 'concept_id_2': concept_id_2, 'top_n': top_n,'ascending':ascending}}
    return json_return

def api_association_obs_exp_ratio(request):
    dataset_id = get_arg_dataset_id(request.args)
    if dataset_id is None:
        return 'dataset_id parameter is missing or imcompatible', 400
    concept_id_1 = get_arg_concept_id(request.args,'concept_id_1')
    if concept_id_1 == []:
        return 'concept_id_1 parameter is missing', 400
    concept_id_2 = get_arg_concept_id(request.args,'concept_id_2')
    domain_id = get_arg_domain_id(request.args)
    top_n = get_arg_top_n(request.args)
    ascending = get_arg_ascending(request.args)
    print(ascending)

    conn = du.sql_connection(CONFIG_FILE)
    cur = conn.cursor()

    results = []
    pair_count = pd.DataFrame(du.get_pair_concept_count(cur=cur,dataset_id=dataset_id,domain_id=domain_id, concept_id_list_1=concept_id_1,concept_id_list_2=concept_id_2))
    if pair_count.shape[0] > 0:
        # calculate obs_exp_ratio
        patient_count = du.get_total_patient_count(cur=cur,dataset_id=dataset_id)
        total_pair_count = du.get_total_pair_count(cur, dataset_id,domain_id=domain_id)
        pair_count['pts'] = float(patient_count[0]['count'])
        # pair_count['pc'] = float(total_pair_count[0]['pair_count'])
        pair_count['expected_count'] = pair_count['concept_count_1'] * pair_count['concept_count_2'] / pair_count['pts']
        pair_count['observed_count'] = pair_count['concept_pair_count']
        pair_count['ln_ratio'] = np.log(pair_count['observed_count'] / pair_count['expected_count'])

        concept_list_1 = list(set(pair_count['concept_id_1'].tolist()))
        concept_details_1 = pd.DataFrame(du.get_omop_id(cur=cur,concept_id_list=concept_list_1))
        concept_details_1 = concept_details_1.rename(columns={'concept_id': 'concept_id_1','concept_name':'concept_name_1','concept_code':'concept_code_1','domain_id':'domain_id_1','vocabulary_id':'vocabulary_id_1'})
        
        # get weighted score.
        pair_count = _get_weighted_statistics(cur=cur,dataset_id=dataset_id,domain_id = domain_id,concept_id_1 = concept_list_1, pair_count_df = pair_count, json_key = 'ln_ratio')        
        high_level_summary = pair_count.groupby('concept_id_2')['ln_ratio'].agg('sum').reset_index()
        high_level_summary = high_level_summary.rename(columns={'ln_ratio': 'ws_ln_ratio'}).sort_values('ws_ln_ratio',ascending=ascending).head(top_n)
        concept_list_2 = list(set(high_level_summary['concept_id_2'].tolist()))
        concept_details_2 = pd.DataFrame(du.get_omop_id(cur=cur,concept_id_list=concept_list_2))
        concept_details_2 = concept_details_2.rename(columns={'concept_id': 'concept_id_2','concept_name':'concept_name_2','concept_code':'concept_code_2','domain_id':'domain_id_2','vocabulary_id':'vocabulary_id_2'})
        detailed_results = pair_count.merge(concept_details_1)
        results = high_level_summary.merge(detailed_results).groupby(['concept_id_2','ws_ln_ratio'])['concept_id_1','concept_name_1','concept_code_1','domain_id_1','vocabulary_id_1','concept_pair_count','w','ln_ratio','expected_count','observed_count'].apply(lambda x: x.to_dict('records')).reset_index(name='z_details')
        results = results.merge(concept_details_2).sort_values('ws_ln_ratio',ascending=ascending)
        results = results.to_dict('records')
    json_return = {'results': results, 'parameter':{'dataset_id':dataset_id, 'domain_id': domain_id, 'concept_id_1': concept_id_1, 'concept_id_2': concept_id_2, 'top_n': top_n, 'ascending': ascending}}
    return json_return

def api_association_relative_frequency(request):
    dataset_id = get_arg_dataset_id(request.args)
    if dataset_id is None:
        return 'dataset_id parameter is missing or imcompatible', 400
    concept_id_1 = get_arg_concept_id(request.args,'concept_id_1')
    if concept_id_1 == []:
        return 'concept_id_1 parameter is missing', 400
    concept_id_2 = get_arg_concept_id(request.args,'concept_id_2')
    domain_id = get_arg_domain_id(request.args)
    top_n = get_arg_top_n(request.args)
    ascending = get_arg_ascending(request.args)

    conn = du.sql_connection(CONFIG_FILE)
    cur = conn.cursor()

    results = []
    pair_count = pd.DataFrame(du.get_pair_concept_count(cur=cur,dataset_id=dataset_id,domain_id=domain_id, concept_id_list_1=concept_id_1,concept_id_list_2=concept_id_2))
    if pair_count.shape[0] > 0:
        # calculate relative_frequency
        pair_count['relative_frequency'] = pair_count['concept_pair_count'] / pair_count['concept_count_2']

        concept_list_1 = list(set(pair_count['concept_id_1'].tolist()))
        concept_details_1 = pd.DataFrame(du.get_omop_id(cur=cur,concept_id_list=concept_list_1))
        concept_details_1 = concept_details_1.rename(columns={'concept_id': 'concept_id_1','concept_name':'concept_name_1','concept_code':'concept_code_1','domain_id':'domain_id_1','vocabulary_id':'vocabulary_id_1'})
        
        # get weighted score.
        pair_count = _get_weighted_statistics(cur=cur,dataset_id=dataset_id,domain_id = domain_id,concept_id_1 = concept_list_1, pair_count_df = pair_count, json_key = 'relative_frequency')        
        high_level_summary = pair_count.groupby('concept_id_2')['relative_frequency'].agg('sum').reset_index()
        high_level_summary = high_level_summary.rename(columns={'relative_frequency': 'ws_relative_frequency'}).sort_values('ws_relative_frequency',ascending=ascending).head(top_n)
        concept_list_2 = list(set(high_level_summary['concept_id_2'].tolist()))
        concept_details_2 = pd.DataFrame(du.get_omop_id(cur=cur,concept_id_list=concept_list_2))
        concept_details_2 = concept_details_2.rename(columns={'concept_id': 'concept_id_2','concept_name':'concept_name_2','concept_code':'concept_code_2','domain_id':'domain_id_2','vocabulary_id':'vocabulary_id_2'})
        detailed_results = pair_count.merge(concept_details_1)
        results = high_level_summary.merge(detailed_results).groupby(['concept_id_2','ws_relative_frequency'])['concept_id_1','concept_name_1','concept_code_1','domain_id_1','vocabulary_id_1','concept_pair_count','relative_frequency'].apply(lambda x: x.to_dict('records')).reset_index(name='z_details')
        results = results.merge(concept_details_2).sort_values('ws_relative_frequency',ascending=ascending)
        results = results.to_dict('records')
    json_return = {'results': results, 'parameter':{'dataset_id':dataset_id, 'domain_id': domain_id, 'concept_id_1': concept_id_1, 'concept_id_2': concept_id_2, 'top_n': top_n,'ascending':ascending}}
    return json_return

def _get_weighted_statistics(cur=None,dataset_id=None,domain_id = None,concept_id_1 = None, pair_count_df = None, json_key = 'jaccard_index'):
    '''
    help function.
    Input 1: original association statistics required
    Input 2: concept_list in the query for weight calculation (currently only support jaccard index based weight calculation.)
    return weighted json_key. e.g. ws_jaccard_index. 
    '''
    concept_list_1_w_df= pd.DataFrame({'concept_id_1':concept_id_1})
    concept_list_1_w_df['w'] = 1
    pair_count_q1 = pd.DataFrame(du.get_pair_concept_count(cur=cur,dataset_id=dataset_id,domain_id=domain_id, concept_id_list_1=concept_id_1,concept_id_list_2=concept_id_1))
    if pair_count_q1.shape[0] > 0:
        pair_count_q1['jaccard_index'] = pair_count_q1['concept_pair_count'] / (pair_count_q1['concept_count_1'] + pair_count_q1['concept_count_2'] - pair_count_q1['concept_pair_count'])
        pair_count_q1 = pair_count_q1.groupby('concept_id_1')['jaccard_index'].agg('sum').reset_index()
        concept_list_1_w_df = concept_list_1_w_df.merge(pair_count_q1).reset_index()
        concept_list_1_w_df['w'] = concept_list_1_w_df['w'] + concept_list_1_w_df['jaccard_index']
    concept_list_1_w_df['w'] = 1/concept_list_1_w_df['w']
    concept_list_1_w_df = concept_list_1_w_df[['concept_id_1','w']]

    pair_count_df = pair_count_df.merge(concept_list_1_w_df)
    pair_count_df[json_key] = pair_count_df['w'] * pair_count_df[json_key]
    pair_count_df = pair_count_df[~pair_count_df['concept_id_2'].isin(concept_id_1)]
    return pair_count_df

def get_arg_dataset_id(args):
    dataset_id = args.get('dataset_id')
    if dataset_id is None or dataset_id.isspace() or not dataset_id.strip().isdigit():
        dataset_id = None
    else:
        dataset_id = int(dataset_id.strip())
    return dataset_id

def get_arg_top_n(args, default_top_n=TOP_N_DEFAULT):
    top_n = args.get('top_n')
    if top_n is None or top_n.isspace() or not top_n.strip().isdigit():
        top_n = default_top_n
    else:
        top_n = int(top_n.strip())
    return top_n

def get_arg_ascending(args, default_ascending=ASCENDING_DEFAULT):
    ascending = args.get('ascending')
    if ascending is None:
        top_n = default_ascending
    elif ascending.strip().lower() in ['true', '1', 't']:
       ascending = True
    else:
       ascending = False
    return ascending

def get_arg_q(args,q_name='q'):
    q = args.get(q_name)
    if q is None or q.isspace():
        q = []
    else:
        q = list(set(q.split(';')))
    return q

def get_arg_domain_id(args):
    domain_id = args.get('domain_id')
    print(domain_id)
    if domain_id is None or (domain_id not in ['phenotypes','diseases']):
        domain_id = None
    return domain_id

def get_arg_concept_id(args, param_name='concept_id'):
    concept_id = args.get(param_name)
    if concept_id is None:
        concept_id = []
    else:
        concept_id = [int(c.strip()) for c in concept_id.split(";") if c.strip().isdigit()]
    return concept_id


# def get_arg_int(args, param_name):
#     param = args.get(param_name)
#     if param is None or param == [''] or not param.strip().isnumeric():
#         return None
#     else:
#         try:
#             return int(param.strip())
#         except ValueError:
#             return None


# def get_arg_float(args, param_name):
#     param = args.get(param_name)
#     if param is None or param == ['']:
#         return None
#     else:
#         try:
#             return float(param.strip())
#         except ValueError:
#             return None


# def get_arg_boolean(args, param_name):
#     param = args.get(param_name)
#     if param is None or param == ['']:
#         return None
#     else:
#         try:
#             return param.strip().lower() in ['true', '1', 't']
#         except AttributeError:
#             return None
#     return None

# def get_arg_hierarchical(args, default_hierarchical=DEFAULT_HIERARCHICAL):
#     hierarchical = args.get('hierarchical')
#     if hierarchical is None or hierarchical.isspace() or not hierarchical.strip().isdigit():
#         hierarchical = default_hierarchical
#     else:
#         hierarchical = int(default_hierarchical.strip())
#     return hierarchical

