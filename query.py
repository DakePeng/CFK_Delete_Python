import sys
'''
    make a given query to the bigQuery database specified in the global variable "address"
    @query: a string of the SQL query to make
    
    @return: the result of the query
'''
def make_query(query):
    log_message = "Making query: " + str(query)
    try:
        from google.cloud import bigquery
        client = bigquery.Client(project= "carlfilekeeper-database")
        query_job = client.query(query)  # API request
        log_message += " ------ succeded"
        print(log_message)
        return query_job.result()  # Waits for query to finish
    except Exception as error:
        log_message += " ------ failed, error message: " + str(error)
        print(log_message)
        print(log_message, file = sys.stderr)
