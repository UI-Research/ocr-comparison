import json
import os
import boto3
import time
import pandas as pd

# First, use AWS CLI to upload data to an s3 bucket. 
# aws s3 cp comparison-input-data s3://bucket-name/sub-folder --recursive

def startJob(s3BucketName, objectName, prefix):
    '''
    Runs Textract's StartDocumentAnalysis action and
    specifies an s3 bucket to dump output
    '''
    response = None
    client = boto3.client('textract')
    response = client.start_document_analysis(
        DocumentLocation = {
            'S3Object': {
                'Bucket': s3BucketName,
                'Name': objectName
            }
        },
        FeatureTypes = ['TABLES'], #TABLES + FORMS is much more expensive ($0.065 per page instead of 0.015)
        OutputConfig =  {
                'S3Bucket': s3BucketName,
                'S3Prefix': prefix
        }
    )

    return response["JobId"]

def isJobComplete(jobId):
    ''''
    Checks whether document analysis still in progress
    '''
    time.sleep(5)
    client = boto3.client('textract')
    response = client.get_document_analysis(JobId=jobId)
    status = response["JobStatus"]
    print("Job status: {}".format(status))

    while(status == "IN_PROGRESS"):
        time.sleep(5)
        response = client.get_document_analysis(JobId=jobId)
        status = response["JobStatus"]

    return status

def getJobResults(jobId):
    '''
    If document analysis complete, runs Textract's GetDocumentAnalysis action
    and pulls JSON results to be stored in s3 bucket designated above
    '''

    pages = []


    client = boto3.client('textract')
    response = client.get_document_analysis(JobId=jobId)
    
    pages.append(response)

    nextToken = None
    if('NextToken' in response):
        nextToken = response['NextToken']

    while(nextToken):

        response = client.get_document_analysis(JobId=jobId, NextToken=nextToken)

        pages.append(response)
        
        nextToken = None
        if('NextToken' in response):
            nextToken = response['NextToken']

    return pages




def run_textract_all(s3Bucket, s3BucketName):
    '''
    Runs complete document analysis for all docs in folder
    '''

    total_time = 0
    filter_prefix = "comparison-input-data"
    for obj in s3Bucket.objects.filter(Prefix=filter_prefix):
        start = time.time()

        documentName = obj.key
        path, filename = os.path.split(obj.key)
        prefix = "comparison-output-data/{}".format(filename[:-4])
       
        print('Started job for {}...'.format(filename))
        jobId = startJob(s3BucketName, documentName, prefix)
        if(isJobComplete(jobId)):
            getJobResults(jobId)

        end = time.time()
        print("Finished job for {} in {} seconds\n".format(filename, round(end-start, 2)))
        total_time += (end-start)
    print('Total runtime: {} seconds'.format(round(total_time, 2)))



def download_locally(filename, s3BucketName):
    '''
    Downloads all JSONs for a town to local folder;
    won't use this once EC2 instance is spun up
    '''
    s3 = boto3.resource('s3')
    s3_bucket = s3BucketName
    local_folder = 'comparison-output-data/{}'.format(filename)
    os.makedirs(local_folder, exist_ok=True)

    my_bucket = s3.Bucket(s3_bucket)

    for obj in my_bucket.objects.filter(Prefix=local_folder):
        path, filename = os.path.split(obj.key)
        my_bucket.download_file(obj.key, "{}/{}.json".format(local_folder, filename))


def extract_bbox(df):
    '''Extracts Bounding Box columns from nested "Geometry" JSON'''
    geom_list = df['Geometry'].to_list()
    bbox = [geom['BoundingBox'] for geom in geom_list]
    bbox_df = pd.DataFrame(bbox).add_prefix('BB_')
    return bbox_df

def extract_polygon(df):
    '''Extracts Polygon columns from nested "Geometry" JSON'''
    geom_list = df['Geometry'].to_list()
    poly_df = pd.DataFrame()
    for point in range(4):
        poly = pd.DataFrame([geom['Polygon'][point] for geom in geom_list]).add_prefix('Poly_').add_suffix('{}'.format(point))
        poly_df = pd.concat([poly_df, poly], axis=1)
    return poly_df

def extract_relationship(relationship, type='CHILD'):
    '''
    Extracts relationship types from nested "Relationships" JSON;
    Can specify either 'CHILD' or 'VALUE' as the type;
    Returns list of relationships for a given block when they exist
    '''
    if relationship is None or relationship[0]['Type'] != type:
        return None
    else:
        return relationship[0]['Ids']

def import_file(filename, s3BucketName, download=False):
    '''
    Takes in all JSON files from Textract for a given file (in string format);
    Returns one pandas dataframe after parsing/combining JSONs
    and applying above cleaning functions;
    '''
    if download:
        print('Starting local download for {}...'.format(filename))
        download_locally(filename, s3BucketName)

    local_folder = 'comparison-output-data/{}'.format(filename)
    dict_list = []
    
    for file in range(len(os.listdir(local_folder))-1):
        data = json.load(open('{}/{}.json'.format(local_folder, file+1)))['Blocks']
        dict_list.extend(data)  

    df = pd.DataFrame(dict_list)
    if len(df) == 0:
        print('No doc exists in the bucket!')
        return None
    bbox = extract_bbox(df)
    
    poly = extract_polygon(df)
    
    children = df['Relationships'].apply(extract_relationship, type='CHILD').rename('relat_children')
    values = df['Relationships'].apply(extract_relationship, type='VALUE').rename('relat_values')

    clean_df = pd.concat([df, bbox, poly, children, values], axis=1).drop('Geometry',axis=1)    
    
    return clean_df

if __name__ == "__main__":
    s3BucketName = "[ENTER BUCKET NAME]"
    s3 = boto3.resource('s3')
    s3_bucket = s3.Bucket(s3BucketName)

    run_textract_all(s3_bucket, s3BucketName)

 
    files = ['scan1', 'scan2', 'scan3']
    for f in files:
        df = import_file(f, s3BucketName, download=True)
    
        lines = [line for (line, blocktype) in zip(df['Text'], df['BlockType']) if blocktype == 'LINE']
        textfile = open('comparison-output-data/textract/{}.txt'.format(f), 'w')
        for line in lines:
            textfile.write(line + "\n")
        textfile.close()