import pymysql



def sql_connection(config_file):
    # Connect to MySQL database
    # print u"Connecting to MySQL database"
    return pymysql.connect(read_default_file=config_file,
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)

def get_datasets(cur=None):
    sql = '''SELECT * 
                FROM dataset;'''
    cur.execute(sql)
    return cur.fetchall()

def get_domain_counts(cur=None,dataset_id = 2):
    sql = '''SELECT * 
                FROM domain_concept_counts 
                WHERE dataset_id=%(dataset_id)s;'''
    params = {'dataset_id': dataset_id}
    cur.execute(sql, params)
    return cur.fetchall()

def get_domain_pair_counts(cur=None,dataset_id = 2):
    sql = '''SELECT * 
                FROM domain_pair_concept_counts 
                WHERE dataset_id=%(dataset_id)s;'''
    params = {'dataset_id': dataset_id}
    cur.execute(sql, params)
    return cur.fetchall()

def get_total_pair_count(cur = None, dataset_id = 2,domain_id = None):
    sql = '''SELECT SUM(count) AS pair_count
            FROM domain_pair_concept_counts
            WHERE dataset_id = %(dataset_id)s
            {domain_filter}
            ;'''
    params = {'dataset_id': dataset_id}
     # Filter concepts by domain
    if domain_id is None or domain_id == [''] or domain_id.isspace():
        domain_filter = ''
    else:
        domain_filter = 'AND (domain_id_1 = %(domain_id)s OR domain_id_2 = %(domain_id)s )'
        params['domain_id'] = domain_id
    sql = sql.format(domain_filter=domain_filter)
    cur.execute(sql, params)
    return cur.fetchall()

def get_omop_id(cur = None, concept_id_list = None, concept_name_list = None, concept_code_list = None, domain_id = None, vocabulary_id = None):
    sql = '''SELECT distinct c.concept_id,c.concept_name,c.concept_code,c.domain_id,c.vocabulary_id 
                FROM concept c
                LEFT JOIN map_oxo mo
                ON c.concept_code = mo.curie_1
                WHERE standard_concept IN ('S','C') 
                    {domain_filter}
                    {vocabulary_filter}
                    {id_name_code_filter}
                LIMIT 100;
    '''
    params = {
        
    }

    # Filter concepts by concept_name
    if concept_name_list is None or concept_name_list == ['']:
        concept_name_filter = ''
    else:
        concept_name_filter_or_clause = 'OR'.join([''' (concept_name like '%%''' + cn + '''%%') ''' for cn in concept_name_list])
        concept_name_filter = '(' + concept_name_filter_or_clause + ')'

    # Filter concepts by concept_id
    if concept_id_list is None or concept_id_list == ['']:
        concept_id_filter = ''
    else:
        concept_id_filter_clause = ','.join(["'" + str(ci)  + "'" for ci in concept_id_list])
        concept_id_filter = '( c.concept_id IN (' + concept_id_filter_clause + ') )'


    # Filter concepts by concept_code
    if concept_code_list is None or concept_code_list == ['']:
        concept_code_filter = ''
    else:
        concept_code_filter_clause = ','.join(["'" + cc  + "'" for cc in concept_code_list])
        concept_code_filter = '( concept_code IN (' + concept_code_filter_clause + ') OR curie_2 IN (' + concept_code_filter_clause + '))'

    # merge code, name, id filters with OR
    id_name_code_filter = ' OR '.join([i for i in [concept_name_filter,concept_code_filter,concept_id_filter] if len(i) > 0])
    if id_name_code_filter == '':
        print("at list one of the following should be provided: concept_name, concept_id, concept_code")
        return tuple()
    else:
        id_name_code_filter = 'AND (' + id_name_code_filter + ')'

    # Filter concepts by domain
    if domain_id is None or domain_id == [''] or domain_id.isspace():
        domain_filter = ''
    else:
        domain_filter = 'AND domain_id = %(domain_id)s'
        params['domain_id'] = domain_id

    # Filter concepts by vocabulary
    if vocabulary_id is None or vocabulary_id == [''] or vocabulary_id.isspace():
        vocabulary_filter = ''
    else:
        vocabulary_filter = 'AND vocabulary_id = %(vocabulary_id)s'
        params['vocabulary_id'] = vocabulary_id

    sql = sql.format(id_name_code_filter = id_name_code_filter, domain_filter=domain_filter, vocabulary_filter=vocabulary_filter)
    cur.execute(sql, params)
    return cur.fetchall()

def get_total_patient_count(cur = None, dataset_id = 3):
    sql = '''SELECT *
                FROM patient_count 
                WHERE dataset_id=%(dataset_id)s;'''
    params = {'dataset_id': dataset_id}
    cur.execute(sql, params)
    return cur.fetchall()

def get_single_concept_count(cur = None, concept_id_list = [], dataset_id = 3, domain_id = None, top_n = 999999):
    params = {
            'dataset_id': dataset_id,
    }
    if len(concept_id_list) > 0:
        sql = '''
            SELECT
                c.concept_id as concept_id,
                c.concept_count as concept_count
                FROM concept_counts c
                INNER JOIN concept con on con.concept_id = c.concept_id
                WHERE c.dataset_id = %(dataset_id)s 
                AND c.concept_id in ({concept_id_filter})
        '''
        concept_id_filter = ','.join([str(c) for c in concept_id_list])
        sql = sql.format(concept_id_filter = concept_id_filter)
    else:
        sql = '''
            SELECT
                c.concept_id as concept_id,
                c.concept_count as concept_count
                FROM concept_counts c
                LEFT JOIN concept as con
                on c.concept_id = con.concept_id
                WHERE c.dataset_id = %(dataset_id)s 
                {domain_filter}
                ORDER BY concept_count DESC
                LIMIT {top_n_filter};
        '''
        concept_id_filter = ','.join([str(c) for c in concept_id_list])
        # Filter concepts by domain
        if domain_id is not None:
            domain_filter = 'AND con.domain_id = %(domain_id)s'
            params['domain_id'] = domain_id
        else:
            domain_filter = ''
        sql = sql.format(domain_filter = domain_filter,top_n_filter = top_n)
    print(sql)
    cur.execute(sql, params)
    return cur.fetchall()

def get_pair_concept_count(cur = None, concept_id_list_1 = [], concept_id_list_2 = [], dataset_id = 3,domain_id = None, top_n = 999999):
    sql = '''
        SELECT * FROM
        (
            SELECT
                cp.concept_id_1 as concept_id_1,
                cp.concept_id_2 as concept_id_2,
                cp.concept_count as concept_pair_count,
                c1.concept_count as concept_count_1,
                c2.concept_count as concept_count_2
                FROM concept_pair_counts cp
                INNER JOIN concept_counts c1 ON cp.concept_id_1 = c1.concept_id
                INNER JOIN concept_counts c2 ON cp.concept_id_2 = c2.concept_id
                INNER JOIN concept con on con.concept_id = cp.concept_id_2
                WHERE cp.dataset_id = %(dataset_id)s 
                AND c1.dataset_id = %(dataset_id)s 
                AND c2.dataset_id = %(dataset_id)s
                {concept_id_filter_1}
                {domain_filter}
                GROUP BY concept_id_1, concept_id_2
            UNION 
            SELECT
                cp.concept_id_2 as concept_id_1,
                cp.concept_id_1 as concept_id_2,
                cp.concept_count as concept_pair_count,
                c1.concept_count as concept_count_1,
                c2.concept_count as concept_count_2
                FROM concept_pair_counts cp
                INNER JOIN concept_counts c1 ON cp.concept_id_2 = c1.concept_id
                INNER JOIN concept_counts c2 ON cp.concept_id_1 = c2.concept_id
                INNER JOIN concept con on con.concept_id = cp.concept_id_1
                WHERE cp.dataset_id = %(dataset_id)s 
                AND c1.dataset_id = %(dataset_id)s 
                AND c2.dataset_id = %(dataset_id)s
                {concept_id_filter_2}
                {domain_filter}
                GROUP BY concept_id_1, concept_id_2
        ) x
        ORDER BY x.concept_pair_count DESC
        LIMIT {top_n_filter};
        '''
    params = {
        'dataset_id': dataset_id,
    }
    concept_id_1 = ','.join([str(c) for c in concept_id_list_1])
    if len(concept_id_list_2) > 0:
        concept_id_2 = ','.join([str(c) for c in concept_id_list_2])
        concept_id_filter_1 = '''
            AND (
                (cp.concept_id_1 in ({concept_id_1}) AND cp.concept_id_2 in ({concept_id_2}) )
            )
        '''
        concept_id_filter_2 = '''
            AND (
                (cp.concept_id_2 in ({concept_id_1}) AND cp.concept_id_1 in ({concept_id_2}) )
            )
        '''
        concept_id_filter_1 = concept_id_filter_1.format(concept_id_1= concept_id_1, concept_id_2 = concept_id_2)
        concept_id_filter_2 = concept_id_filter_2.format(concept_id_1= concept_id_1, concept_id_2 = concept_id_2)
    else:
        concept_id_filter_1 = '''
            AND (
                (cp.concept_id_1 in ({concept_id_1}) )
            )
        '''
        concept_id_filter_2 = '''
            AND (
                (cp.concept_id_2 in ({concept_id_1}) )
            )
        '''
        concept_id_filter_1 = concept_id_filter_1.format(concept_id_1 = concept_id_1)
        concept_id_filter_2 = concept_id_filter_2.format(concept_id_1 = concept_id_1)
    # Filter concepts by domain
    if domain_id is not None and not domain_id == ['']:
        domain_filter = 'AND con.domain_id = %(domain_id)s'
        params['domain_id'] = domain_id
    else:
        domain_filter = ''
    
    sql = sql.format(concept_id_filter_1 = concept_id_filter_1, concept_id_filter_2 = concept_id_filter_2, domain_filter=domain_filter, top_n_filter = top_n)
    cur.execute(sql, params)
    return cur.fetchall()


if __name__ == '__main__':
    # Configuration
    # log-in credentials for database

    # Connect to MYSQL database
    conn = sql_connection()
    cur = conn.cursor()
    # print(get_datasets(cur))
    # print(get_domain_counts(cur))
    # print(get_domain_pair_counts(cur))
    # print(get_total_pair_count(cur))
    # print(get_omop_id(cur,concept_id_list=[90001263,90003560]))
    # print(get_omop_id(cur,concept_id_list=[90001263,'HP:0003560']))
    # print(get_omop_id(cur,concept_id_list=[90001263,'HP:0003560'],concept_code_list=['HP:0003560']))
    # print(get_omop_id(cur,concept_id_list=[90001263,'HP:0003560'],concept_code_list=['HP:0003560'],domain_id = 'phenotypes'))
    # print(get_omop_id(cur,concept_id_list=[90001263,'HP:0003560'],concept_code_list=['HP:0003560'],vocabulary_id = 'hpo'))
    # print(get_omop_id(cur))
    # print(get_omop_id(cur,concept_id_list=[90001263,'HP:0003560'],concept_code_list=['HP:0003560'],concept_name_list=['muscular dystr']))
    # print(get_total_patient_count(cur,dataset_id=2))
    # print(get_single_concept_count(cur,dataset_id=3,concept_id_list=[90003560,90001263]))
    # print(get_single_concept_count(cur,dataset_id=3,concept_id_list=[90001263]))
    # print(get_single_concept_count(cur,dataset_id=3))
    # print(get_pair_concept_count(cur,concept_id_list_1 = [90001263,90003560],dataset_id=3))
    # print(get_pair_concept_count(cur,concept_id_list_1 = ['90001263',90003560],dataset_id=3))
    print(get_pair_concept_count(cur,concept_id_list_1 = [90001263,90003560],concept_id_list_2 = [90003560,90031797],dataset_id=3))



