#!/usr/bin/python3

import signal
import time
import threading
import requests
import json
import pymongo

client = pymongo.MongoClient("localhost", 27017)
db = client.facebook
pagesColl = db.pages
postsColl = db.posts
reactionsColl = db.reactions
commentsColl = db.comments

app_id = ''
app_secret = ''
token = ''

base_url = 'https://graph.facebook.com/v2.9/'

kill_now = False

# TODO: handle errors when sending requests

class Scraper:
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        global kill_now
        kill_now = True

    def fetch_posts(self, page_id):
        global kill_now
        # TODO: revisar si hay que poner todo en minusculas y quitar acentos    
        # TODO: extraer posts nuevos, buscar la fecha mas reciente que se busco
        # TODO: poner _id como el id del post/comment/page
        last_date = '2016-01-01' # TODO: cambiar por el verdadero last date
        request_url = base_url + page_id + '/posts?fields=created_time,story,message,name,description&pretty=0&since=' + last_date + '&limit=100&access_token=' + token
        posts = requests.get(request_url).json()

        # Keep getting posts until we've reached the end
        while True:
            try:
                #print("Fetching posts for " + page_id)
                #print(posts)
                # Perform some action on each post in the collection we receive from
                # Facebook.

                #print("Fetching reactions for " + page_id)


                #print("Fetching comments for " + page_id)

                reactions = []
                comments = []
                for i, post in enumerate(posts['data']):
                    #print("i = ", i, ", post = ", post)
                    reactions.append(self.fetch_reactions(post['id']))
                    comments.extend(self.fetch_comments(post['id']))
                    #print("comments = ", comments)
                    #print(posts['data'][i])
                    #posts['data'][i]['reactions'] = reactions
                    #print("posts[i] = ", posts['data'][i]['reactions'])
                    #comments = self.fetch_comments(post['id'])
                #comments, reactions = [self.fetch_comments_and_reactions(post['id']) for post in posts['data']]

                result = postsColl.insert_many(posts['data'])
                reactionsColl.insert_many(reactions)
                commentsColl.insert_many(comments)
                
                if kill_now:
                    print("Exiting in 5 seconds...")
                    time.sleep(5)
                    return
                else:
                    # Attempt to make a request to the next page of data, if it exists.
                    posts = requests.get(posts['paging']['next']).json()

            except KeyError as e:
                # When there are no more pages (['paging']['next']), break from the
                # loop and end the script.
                #traceback.print_exc()
                print(e)
                return
        
        # TODO: Luego extraer posts viejos
    
    def fetch_reactions(self, post_id):
        request_url = base_url + post_id + '?fields=reactions.type(ANGRY).limit(0).summary(1).as(angry),reactions.type(HAHA).limit(0).summary(1).as(haha),reactions.type(LIKE).limit(0).summary(1).as(like),reactions.type(LOVE).limit(0).summary(1).as(love),reactions.type(SAD).limit(0).summary(1).as(sad),reactions.type(WOW).limit(0).summary(1).as(wow)&access_token=' + token
        reactions = requests.get(request_url).json()
        #print("reactions for " + post_id + ": ", reactions)
        return reactions

    def fetch_comments(self, post_id):
        request_url = base_url + post_id + '/comments?fields=created_time,message,id,like_count&limit=100&access_token=' + token

        comms = requests.get(request_url).json()
        comments = comms['data']
        #print("comments = ", comments)
        # Keep getting posts until we've reached the end
        while True:
            try:
                comms = requests.get(comms['paging']['next']).json()
                comments.extend(comms['data'])

            except KeyError:
                # When there are no more pages (['paging']['next']), break from the
                # loop and end the script.
                print("No more ['paging']['next'] for comments")
                break

        return comments


if __name__ == '__main__':
    # TODO: verificar env variable de config antes
    with open('config.json') as config:
        data = json.load(config)
    
    app_id = data['credentials']['appId']
    app_secret = data['credentials']['appSecret']
    token = app_id + '|' + app_secret
    
    threads = []
    scrapers = []
    num_threads = len(data['pages'])

    for i in range(len(data['pages'])):
        scrapers.append(Scraper())
        page_id = str(data['pages'][i]['id'])
        print("page ", i, " = " + page_id)
        
        thread = threading.Thread(target=scrapers[i].fetch_posts, args=(page_id,))
        threads.append(thread)
        threads[i].start()

    for thread in threads:
        thread.join()

    # TODO: verificar si en la base de datos ya existe la pagina para volver a buscar
    #scraper = Scraper()

    #page_id = '14302129065' # El Espectador

    #scraper.fetch_posts(page_id)

    print("End of the program. Killed gracefully.")
