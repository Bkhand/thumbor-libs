# thumbor_libs_blackhand
Libs for thumbor 7+

## Table of Contents
1. [General purposes] (#General)
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
Thumbor 7.0.x
Python  > 3.7
MongoDB 4.4 / 5
```

# Loaders

1. [pic_nn_loader] (#pic_nn_loader)
2. [pic_nnoh_loader] (#pic_nnoh_loader)
2. [mongodb_gridfs_loader] (#mongodb_gridfs_loader)

## pic_nn_loader

Description: Loader de type file, avec un fallback sur un autre filesystem.

Implementation: 
```
LOADER = thumbor_libs_blackhand.loaders.pic_nn_loader
PIC_LOADER_ROOT_PATH = #root path for file
PIC_LOADER_FALLBACK_PATH = #fallback path for file
PIC_LOADER_MAX_SIZE = #max size in bytes default 16777216
```

## pic_nnoh_loader

Description: Loader de type pic_nn_loader, avec un fallback sur du http/s http_loader.

Implementation: 
```
LOADER = thumbor_libs_blackhand.loaders.pic_nnoh_loader
PIC_LOADER_ROOT_PATH = #root path for file
PIC_LOADER_FALLBACK_PATH = #fallback path for file
PIC_LOADER_MAX_SIZE = #max size in bytes default 16777216

#Ajouter les options additionnelles du LOADER http_loader standard
```

## mongodb_gridfs_loader

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

## mongodb_webp_storage

Description: Stockage des images pour MongoDB/GridFS compatible avec la fonction auto_webp.

Implementation: 
```
STORAGE = 'thumbor_libs_blackhand.storages.mongo_webp_storage'
MONGO_STORAGE_DB = 'thumbor' # MongoDB storage server database name
MONGO_STORAGE_DB = 'thumbor' # MongoDB storage server database name
MONGO_STORAGE_COLLECTION = 'images' # MongoDB storage image collection

```

# Result_storages

## mongodb_webp_result_storage

Description: Mise en cache des images pour MongoDB compatible avec la fonction auto_webp. Attention l'expiration doit être gerée via un index TTL Mongo.

Implementation: 
```
STORAGE = 'thumbor_libs_blackhand.result_storages.mongo_webp_result_storage'
MONGO_RESULT_STORAGE_DB = 'thumbor' # MongoDB storage server database name
MONGO_RESULT_STORAGE_COLLECTION = 'images' # MongoDB storage image collection
```

Options:
```
MONGO_RESULT_STORAGE_MAXCACHESIZE = 15900000 # Max size in Bytes for Binary in doc MongoDB, if 0 deactivated but limited at 16MB BSON
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

## prometheus_metrics

Mise a disposition de metriques pour prometheus

Implementation: 
```
METRICS = 'thumbor_libs_blackhand.metrics.prometheus_metrics'
PROMETHEUS_SCRAPE_PORT = <numéro de port>
```