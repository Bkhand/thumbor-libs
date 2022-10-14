# thumbor_libs_blackhand
Libs for thumbor 7+

## Table of Contents
1. [General](#General)
2. [Loaders](#Loaders)
3. [Storages](#Storages)
4. [Result_storages](#Result_storages)
5. [Url_signers](#Url_signers)
6. [FAQs](#faqs)



# General

Collection de modules pour Thumbor 7+ Python3

Ces libs ne sont pas destinées a tourner en production (absence du stack de test)

Test seulement.


Environnement:
```
Thumbor 7.1.x
Python  3.9
MongoDB 4.4 / 5
```

# Loaders

1. [spec_http_fallback_file_loader] (#spec_http_fallback_file_loader)
2. [specb_http_or_specb_loader] (#specb_http_or_specb_loader)
2. [mongodb_loader] (#mongodb_loader)

## spec_http_fallback_file_loader

Description: Loader de type file, avec un fallback sur un autre filesystem.

Implementation: 
```
LOADER = thumbor_libs_blackhand.loaders.spec_http_fallback_file_loader
PIC_LOADER_ROOT_PATH = #root path for file
PIC_LOADER_FALLBACK_PATH = #fallback path for file
PIC_LOADER_MAX_SIZE = #max size in bytes default 16777216
```

## specb_http_or_specb_loader

Description: Loader de type spec_http_fallback_file_loader, avec un fallback sur du http/s http_loader.

Implementation: 
```
LOADER = thumbor_libs_blackhand.loaders.specb_http_or_specb_loader
PIC_LOADER_ROOT_PATH = #root path for file
PIC_LOADER_FALLBACK_PATH = #fallback path for file
PIC_LOADER_MAX_SIZE = #max size in bytes default 16777216

#Ajouter les options additionnelles du LOADER http_loader standard
```

## mongodb_loader

Description: Loader pour MongoDB/Gridfs.

Implementation: 
```
LOADER = 'thumbor_libs_blackhand.loaders.mongodb_loader'
MONGO_ORIGIN_DB = 'thumbor' # MongoDB loader database name
MONGO_ORIGIN_COLLECTION = '<nom de la collection>' #host
MONGO_ORIGIN_URI = 'url de connection vers mongoDB mongodb://'
```

Url type: 
```
https://thumbor-server.domain/[secret|unsafe]/[params]/XXXXXXXXXXXXXXXXXXXXXX[/.../..../.xxx  <= all is facultative after id ]
where `XXXXXXXXXXXXXXXXXXXXXX` is a GridFS `file_id`
```

Note: avec utilisation de Varnish quelques modifs sont réaliser
```
##### Configuration example for varnish (recv) with AUTO_WEBP ####
if (req.http.Accept ~ "image/webp") {
  set req.http.Accept = "image/webp";
} else {
  # not present, and we don't care about the rest
  unset req.http.Accept;
}
```

# storages

## mongodb_webp_storage (LEGACY)

Description: Stockage des images pour MongoDB/GridFS compatible avec la fonction auto_webp.

Implementation: 
```
STORAGE = 'thumbor_libs_blackhand.storages.mongo_webp_storage'
MONGO_STORAGE_DB = 'thumbor' # MongoDB storage server database name
MONGO_STORAGE_DB = 'thumbor' # MongoDB storage server database name
MONGO_STORAGE_COLLECTION = 'images' # MongoDB storage image collection

```

# Result_storages

## mongodb_webp_result_storage / mongodb_legacy_result_storage, (LEGACY DEPRECATED)

Description: Mise en cache des images pour MongoDB compatible avec la fonction auto_webp. Attention l'expiration doit être gerée via un index TTL Mongo.

Implementation:
```
RESULT_STORAGE = 'thumbor_libs_blackhand.result_storages.mongodb_[webp|legacy]_result_storage'
MONGO_RESULT_STORAGE_SERVER_AUTH = "auth base in mongodb"
MONGO_RESULT_STORAGE_SERVER_COLLECTION = "collection to store image & metadata"
MONGO_RESULT_STORAGE_SERVER_DB = "base mongodb"
MONGO_RESULT_STORAGE_SERVER_HOST = "host1,host2 ..."
MONGO_RESULT_STORAGE_SERVER_PASSWORD = "password"
MONGO_RESULT_STORAGE_SERVER_PORT = "27017"
MONGO_RESULT_STORAGE_SERVER_READ_PREFERENCE = "secondaryPreferred"
MONGO_RESULT_STORAGE_SERVER_REPLICASET = "name of replicaset"
MONGO_RESULT_STORAGE_SERVER_USER = "user"
```

Options:
```
MONGO_RESULT_STORAGE_MAXCACHESIZE = 15900000 # Max size in Bytes for Binary in doc MongoDB, if 0 deactivated but limited at 16MB BSON
```

## mongodb_result_storage

Description: Mise en cache des images pour MongoDB compatible avec la fonction auto_webp. Attention l'expiration doit être gerée via un index TTL Mongo.

Implementation: 
```
RESULT_STORAGE = 'thumbor_libs_blackhand.result_storages.mongo_result_storage'
MONGO_RESULT_STORAGE_SERVER_AUTH = "auth base in mongodb"
MONGO_RESULT_STORAGE_SERVER_COLLECTION = "collection to store image & metadata"
MONGO_RESULT_STORAGE_SERVER_DB = "base mongodb"
MONGO_RESULT_STORAGE_SERVER_HOSTS = "host1,host2 ..."
MONGO_RESULT_STORAGE_SERVER_PASSWORD = "password"
MONGO_RESULT_STORAGE_SERVER_PORT = "27017"
MONGO_RESULT_STORAGE_SERVER_READ_PREFERENCE = "secondaryPreferred"
MONGO_RESULT_STORAGE_SERVER_REPLICASET = "name of replicaset"
MONGO_RESULT_STORAGE_SERVER_USER = "user"
```


## hybrid_result_storage

Description: Mise en cache des images pour MongoDB (metadata) + disk (binaire) compatible avec la fonction auto_webp. Attention l'expiration doit être gerée via un index TTL Mongo - hors disque TODO.

Implementation: 
```
RESULT_STORAGE = 'thumbor_libs_blackhand.result_storages.mongo_result_storage'
MONGO_RESULT_STORAGE_SERVER_AUTH = "auth base in mongodb"
MONGO_RESULT_STORAGE_SERVER_COLLECTION = "collection to store image & metadata"
MONGO_RESULT_STORAGE_SERVER_DB = "base mongodb"
MONGO_RESULT_STORAGE_SERVER_HOSTS = "host1,host2 ..."
MONGO_RESULT_STORAGE_SERVER_PASSWORD = "password"
MONGO_RESULT_STORAGE_SERVER_PORT = "27017"
MONGO_RESULT_STORAGE_SERVER_READ_PREFERENCE = "secondaryPreferred"
MONGO_RESULT_STORAGE_SERVER_REPLICASET = "name of replicaset"
MONGO_RESULT_STORAGE_SERVER_USER = "user"
CACHE_PATH = "path du storage du cache"
```

Options:
```
MONGO_STORE_METADATA = True
```


Note: avec utilisation de Varnish quelques modifs sont réaliser

Exemple: https://www.fastly.com/blog/test-new-encodings-fastly-including-webp

```
sub vcl_recv {
  # Normalize Accept, we're only interested in webp right now.
  # And only normalize for URLs we care about.
  if (req.http.Accept && req.url ~ "(\.jpe?g|\.png)($|\?)") {
    # So we don't have to keep using the above regex multiple times.
    set req.http.X-Is-An-Image-URL = "yay";

    # Test Le wep n'est pas acceptable
    if (req.http.Accept ~ "image/webp[^,];q=0(\.0?0?0?)?[^0-9]($|[,;])") {
      unset req.http.Accept;
    }

    # Le webp est acceptable
    if (req.http.Accept ~ "image/webp") {
      set req.http.Accept = "image/webp";
    } else {
      # Header non present
      unset req.http.Accept;
    }
  }
#FASTLY recv
}

sub vcl_miss {
  # Si vous avez /foo/bar.jpeg, vous pouvez aussi avoir /foo/bar.webp

  if (req.http.Accept ~ "image/webp" && req.http.X-Is-An-Image-URL) {
    set bereq.url = regsuball(bereq.url, "(\.jpe?g|\.png)($|\?)", ".webp\2");
  }
#FASTLY miss
}

sub vcl_fetch {
  if (req.http.X-Is-An-Image-URL) {
    if (!beresp.http.Vary ~ "(^|\s|,)Accept($|\s|,)") {
      if (beresp.http.Vary) {
        set beresp.http.Vary = beresp.http.Vary ", Accept";
      } else {
         set beresp.http.Vary = "Accept";
      }
    }
  }
#FASTLY fetch
}
```

# Url_signers

## base64_hmac_sha1_trim

Description: Url signers basique avec fonction trim.

Implementation: 
```
URL_SIGNER = 'thumbor_libs_blackhand.url_signers.base64_hmac_sha1_trim'
```

# Metrics

