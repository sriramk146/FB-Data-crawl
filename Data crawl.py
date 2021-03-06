import urllib
import json
import datetime
import csv
import time

def unicode_normalize(text):
    return text.translate({ 0x2018:0x27, 0x2019:0x27, 0x201C:0x22, 0x201D:0x22,
                            0xa0:0x20 }).encode('utf-8')


def request_data_from_url(url):
    req = urllib.Request(url)
    success = False
    while success is False:
        try: 
            #open the url
            response = urllib.urlopen(req)
            
            #200 is the success code for http
            if response.getcode() == 200:
                success = True
        except Exception:
            #if we didn't get a success, then print the error and wait 5 seconds before trying again
            print ('e')
            time.sleep(5)

            print ("Error for URL %s: %s") % (url, datetime.datetime.now())
            print ("Retrying...")

    #return the contents of the response
    return response.read()

def process_post(post, access_token):

    post_id = post['id']
    
    post_message = '' if 'message' not in post.keys() else \
            unicode_normalize(post['message'])
        
    post_type = post['type']

    #for datetime info, we need a few extra steps
    #first convert the given datetime into the format we want
    post_published = datetime.datetime.strptime(
            post['created_time'],'%Y-%m-%dT%H:%M:%S+0000')
    #then account for the time difference between the returned time and my time zone
    post_published = post_published + \
            datetime.timedelta(hours=-2)
    #last, convert the datetime into a string in a format convenient for spreadsheets
    post_published = post_published.strftime(
            '%Y-%m-%d %H:%M:%S')
    #here we call a separate API for information about reactions based on the post's post_id
    #but only if this post is afer the day when reactions first appeared on facebook
   
    #return a list of all the fields we asked for
    return (post_id, post_message, post_type,
            post_published, num_reactions, num_comments, num_shares)

def scrape_facebook_page(page_id, access_token):
    #open up a csv (comma separated values) file to write data to
    with open('%s_facebook_posts.csv' % page_id, 'wb') as file:
        #let w represent our file
        w = csv.writer(file)
        
        #write the header row
        w.writerow(["post_id", "post_message", "post_type",
                    "post_published", "num_reactions", 
                    "num_comments", "num_shares"])

        has_next_page = True
        num_processed = 0  
        scrape_starttime = datetime.datetime.now()

        print ("Scraping %s Facebook Page: %s\n") % (page_id, scrape_starttime)

        #get first batch of posts
        posts = get_facebook_page_data(page_id, access_token)

        #while there is another page of posts to process
        while has_next_page:
            #we just limit to 200 posts for simplicity, if you want all the posts, just remove this
            if num_processed == 200:
                break
                 #for each individual post in our retrieved posts ...
            for post in posts['data']:

                #...get post info and write to our spreadsheet
                w.writerow(process_post(post, access_token))
                    
                num_processed += 1

            #if there is a next page of posts to get, then get next page to process
            if 'paging' in posts.keys():
                posts = json.loads(request_data_from_url(
                                        posts['paging']['next']))
            #otherwise, we are done!
            else:
                has_next_page = False


        print ("Completed!\n%s posts Processed in %s") % \
                (num_processed, datetime.datetime.now() - scrape_starttime)



page_id = input("Please Paste Public Page Name:")

access_token = input("Please Paste Your Access Token:")

if __name__ == '__main__':
    scrape_facebook_page(page_id, access_token)
