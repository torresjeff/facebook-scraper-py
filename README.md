# facebook-scraper-py
Facebook scraper made in Python that stores posts, reactions and comments of a page in a Mongo database.

## Usage
* Create a Facebook app in the [Developer Portal](https://developers.facebook.com/)
* Spin up a MongoDB service in your machine (must be localhost).
* Specify the pages that you want to scrape in a file called `config.json` at the root of the folder

Your `config.json` must look something like this:
```
{
    "credentials": {
        "appId": "<your-app-id>",
        "appSecret": "<your-app-secret>"
    },
    "pages": [
        {"nombre": "Noticias Caracol", "id": 216740968376511},
        {"nombre": "El Tiempo", "id": 148349507804},
        {"nombre": "El Espectador", "id": 14302129065},
        {"nombre": "Noticias RCN", "id": 154413711236788},
        {"nombre": "Revista Semana", "id": 97041406678},
        {"nombre": "El Heraldo", "id": 21935701184},
        {"nombre": "Álvaro Uribe Vélez", "id": 45242794557},
        {"nombre": "Juan Manuel Santos", "id": 330825443903}
    ]
}
```
* The `credentials` object will store the credentials of your app in Facebook.
* The `pages` array requires only the `id` property, which is the ID of the page you want to scrape. Anything else will be ignored, but it is still a good idea to at least put the name of the page to know what you're referencing.
* You can find the page ID by going to [Find my Facebook ID](https://findmyfbid.com/) and entering the link of the page.

The script will create a new Mongo database with the name `facebook` and the following collections:
* `posts`
* `comments`
* `reactions`
