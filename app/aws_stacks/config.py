SMILE_CDR_DEFAULT_PROPERTIES = """
################################################################################
# Node Configuration
################################################################################
node.id                                                                                    =Master
# Set node.config.locked to true to prevent changes to module configuration
node.config.locked                                                                         =false
# Set node.security.strict to enforce strict security (e.g. prevent anonymous superuser privileges)
node.security.strict                                                                       =false


################################################################################
# Cluster Manager Configuration
################################################################################
# Valid options include H2_EMBEDDED, DERBY_EMBEDDED, MYSQL_5_7, MARIADB_10_1, POSTGRES_9_4, ORACLE_12C, MSSQL_2012
module.clustermgr.config.db.driver                                                         =POSTGRES_9_4
module.clustermgr.config.db.url                                                            =jdbc:postgresql://pgsql-clustermgr/clustermgr
module.clustermgr.config.db.username                                                       =postgres
module.clustermgr.config.db.password                                                       =postgres
module.clustermgr.config.db.schema_update_mode                                             =UPDATE
# module.clustermgr.config.db.schema_update_mode                                             =NONE
module.clustermgr.config.stats.heartbeat_persist_frequency_ms                              =15000
module.clustermgr.config.stats.stats_persist_frequency_ms                                  =60000
module.clustermgr.config.stats.stats_cleanup_frequency_ms                                  =300000

# Broker options are EMBEDDED_ACTIVEMQ, REMOTE_ACTIVEMQ, KAFKA, NONE
module.clustermgr.config.messagebroker.type                                                =EMBEDDED_ACTIVEMQ

# Enabling this will cause the cluster manager to always write to its own audit log database, even if you have another audit module defined.
module.clustermgr.config.audit_log.db.always_write_to_clustermgr                           =false

# Request headers to store in the audit log
module.clustermgr.config.audit_log.request_headers_to_store                                =Content-Type,Host

# Seeding for default Keystore
module.clustermgr.config.seed_keystores.file                                               =classpath:/config_seeding/keystores.json

# CDR KAFKA config settings: Prevents timeouts and re-balancing from occurring
module.clustermgr.config.kafka.consumer.properties.file                                    =classpath:/cdr_kafka_config/cdr-kafka-consumer-config.properties
module.clustermgr.config.kafka.producer.properties.file                                    =classpath:/cdr_kafka_config/cdr-kafka-producer-config.properties

# We strongly encourage new customers and installations to leave transaction logs disabled
module.clustermgr.config.transactionlog.enabled                                            =false
module.clustermgr.config.retain_transaction_log_days                                       =7





################################################################################
# Other Modules are Configured Below
################################################################################
# The following setting controls where module configuration is ultimately stored.
# When set to "DATABASE" (which is the default), the clustermgr configuration and Audit module configuration is
# always read but the other modules are stored in the database upon the first
# launch and their configuration is read from the database on subsequent
# launches. When set to "PROPERTIES", values in this file are always used.
#
# In other words, in DATABASE mode, the module definitions below this line are
# only used to seed the database upon the very first startup of the sytem, and
# will be ignored after that. In PROPERTIES mode, the module definitions below
# are read every time the system starts, and existing definitions and config are
# overwritten by what is in this file.
# node.propertysource                                                                        =DATABASE
node.propertysource                                                                        =PROPERTIES

################################################################################
# Database Configuration
################################################################################
module.persistence.type                                                                    =PERSISTENCE_R4
module.persistence.config.db.driver                                                        =POSTGRES_9_4
module.persistence.config.db.url                                                           =jdbc:postgresql://pgsql-persistence/persistence
module.persistence.config.db.username                                                      =postgres
module.persistence.config.db.password                                                      =postgres
# module.persistence.config.db.hibernate_search.directory                                    =./database/lucene_fhir_persistence
module.persistence.config.db.hibernate.showsql                                             =false
module.persistence.config.db.schema_update_mode                                            =UPDATE
# module.persistence.config.db.schema_update_mode                                            =NONE
module.persistence.config.dao_config.expire_search_results_after_minutes                   =60
module.persistence.config.dao_config.allow_multiple_delete.enabled                         =false
module.persistence.config.dao_config.allow_inline_match_url_references.enabled             =true
module.persistence.config.dao_config.allow_external_references.enabled                     =false







################################################################################
# Subscription
################################################################################
module.subscription.type                                                                   =SUBSCRIPTION_MATCHER
module.subscription.requires.PERSISTENCE_ALL                                               =persistence
################################################################################
# Package Registry
################################################################################
module.package_registry.type                                                               =ENDPOINT_PACKAGE_REGISTRY
module.package_registry.requires.PACKAGE_CACHE                                             =persistence
module.package_registry.requires.SECURITY_IN_UP                                            =local_security
module.package_registry.config.port                                                        =8002
module.package_registry.config.tls.enabled                                                 =false
module.package_registry.config.anonymous.access.enabled                                    =true
module.package_registry.config.security.http.basic.enabled                                 =true
################################################################################
# Local Storage Inbound Security
################################################################################
module.local_security.type                                                                 =SECURITY_IN_LOCAL
module.local_security.config.seed.users.file                                               =classpath:/config_seeding/users.json
################################################################################
# ENDPOINT: FHIR Service
################################################################################
module.fhir_endpoint.type                                                                  =ENDPOINT_FHIR_REST
module.fhir_endpoint.requires.PERSISTENCE_ALL                                              =persistence
module.fhir_endpoint.requires.SECURITY_IN_UP                                               =local_security
module.fhir_endpoint.config.port                                                           =8000
module.fhir_endpoint.config.threadpool.min                                                 =2
module.fhir_endpoint.config.threadpool.max                                                 =10
module.fhir_endpoint.config.browser_highlight.enabled                                      =true
module.fhir_endpoint.config.cors.enable                                                    =true
module.fhir_endpoint.config.default_encoding                                               =JSON
module.fhir_endpoint.config.default_pretty_print                                           =true
module.fhir_endpoint.config.base_url.fixed                                                 =http://localhost:8000
module.fhir_endpoint.config.tls.enabled                                                    =false
module.fhir_endpoint.config.anonymous.access.enabled                                       =true
module.fhir_endpoint.config.security.http.basic.enabled                                    =true
module.fhir_endpoint.config.request_validating.enabled                                     =false
module.fhir_endpoint.config.request_validating.fail_on_severity                            =ERROR
module.fhir_endpoint.config.request_validating.tags.enabled                                =false
module.fhir_endpoint.config.request_validating.response_headers.enabled                    =false
module.fhir_endpoint.config.request_validating.require_explicit_profile_definition.enabled =false
################################################################################
# ENDPOINT: JSON Admin Services
################################################################################
module.admin_json.type                                                                     =ADMIN_JSON
module.admin_json.requires.SECURITY_IN_UP                                                  =local_security
module.admin_json.config.port                                                              =9000
module.admin_json.config.tls.enabled                                                       =false
module.admin_json.config.anonymous.access.enabled                                          =true
module.admin_json.config.security.http.basic.enabled                                       =true
################################################################################
# ENDPOINT: Web Admin
################################################################################
module.admin_web.type                                                                      =ADMIN_WEB
module.admin_web.requires.SECURITY_IN_UP                                                   =local_security
module.admin_web.config.port                                                               =9100
module.admin_web.config.tls.enabled                                                        =false
################################################################################
# ENDPOINT: FHIRWeb Console
################################################################################
module.fhirweb_endpoint.type                                                               =ENDPOINT_FHIRWEB
module.fhirweb_endpoint.requires.SECURITY_IN_UP                                            =local_security
module.fhirweb_endpoint.requires.ENDPOINT_FHIR                                             =fhir_endpoint
module.fhirweb_endpoint.config.port                                                        =8001
module.fhirweb_endpoint.config.threadpool.min                                              =2
module.fhirweb_endpoint.config.threadpool.max                                              =10
module.fhirweb_endpoint.config.tls.enabled                                                 =false
module.fhirweb_endpoint.config.anonymous.access.enabled                                    =false
################################################################################
# SMART Security
################################################################################
module.smart_auth.type                                                                     =SECURITY_OUT_SMART
module.smart_auth.requires.CLUSTERMGR                                                      =clustermgr
module.smart_auth.requires.SECURITY_IN_UP                                                  =local_security
module.smart_auth.config.port                                                              =9200
module.smart_auth.config.openid.signing.keystore_id                                        =default-keystore
module.smart_auth.config.issuer.url                                                        =http://localhost:9200
module.smart_auth.config.tls.enabled                                                       =false

#################################################################
# External Audit DB Config
#################################################################
module.audit.type                                                                          =AUDIT_LOG_PERSISTENCE
module.audit.config.db.driver                                                              =POSTGRES_9_4
module.audit.config.db.url                                                                 =jdbc:postgresql://pgsql-audit/audit
module.audit.config.db.username                                                            =postgres
module.audit.config.db.password                                                            =postgres
module.audit.config.db.schema_update_mode                                                  =UPDATE
# module.audit.config.db.schema_update_mode                                                  =NONE
module.audit.config.stats.heartbeat_persist_frequency_ms                                   =15000
module.audit.config.stats.stats_persist_frequency_ms                                       =60000
module.audit.config.stats.stats_cleanup_frequency_ms                                       =300000

#################################################################
# External Transaction Log DB Config
#################################################################
module.transaction.type                                                                          =TRANSACTION_LOG_PERSISTENCE
module.transaction.config.db.driver                                                              =POSTGRES_9_4
module.transaction.config.db.url                                                                 =jdbc:postgresql://pgsql-transaction/transaction
module.transaction.config.db.username                                                            =postgres
module.transaction.config.db.password                                                            =postgres
module.transaction.config.db.schema_update_mode                                                  =UPDATE
# module.transaction.config.db.schema_update_mode                                                  =NONE
module.transaction.config.stats.heartbeat_persist_frequency_ms                                   =15000
module.transaction.config.stats.stats_persist_frequency_ms                                       =60000
module.transaction.config.stats.stats_cleanup_frequency_ms                                       =300000

#################################################################
# License
#################################################################
module.license.type                                                                        =LICENSE
"""


SMILECDR_COMPOSE_YAML = """
services:
  pgsql-clustermgr:
    restart: "unless-stopped"
    image: postgres:17
    container_name: pgsql-clustermgr
    hostname: pgsql-clustermgr
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=clustermgr
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - PGDATA=/var/lib/postgresql/data
    volumes:
      - type: volume
        source: pgsql-clustermgr
        target: /var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready --username=postgres"]
      interval: 1s
      timeout: 1s
      retries: 30
    networks:
      - smilecdr

  pgsql-persistence:
    restart: "unless-stopped"
    image: postgres:17
    container_name: pgsql-persistence
    hostname: pgsql-persistence
    ports:
      - "5433:5432"
    environment:
      - POSTGRES_DB=persistence
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - PGDATA=/var/lib/postgresql/data
    volumes:
      - type: volume
        source: pgsql-persistence
        target: /var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready --username=postgres"]
      interval: 1s
      timeout: 1s
      retries: 30
    networks:
      - smilecdr

  pgsql-audit:
    restart: "unless-stopped"
    image: postgres:17
    container_name: pgsql-audit
    hostname: pgsql-audit
    ports:
      - "5434:5432"
    environment:
      - POSTGRES_DB=audit
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - PGDATA=/var/lib/postgresql/data
    volumes:
      - type: volume
        source: pgsql-audit
        target: /var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready --username=postgres"]
      interval: 1s
      timeout: 1s
      retries: 30
    networks:
      - smilecdr

  pgsql-transaction:
    restart: "unless-stopped"
    image: postgres:17
    container_name: pgsql-transaction
    hostname: pgsql-transaction
    ports:
      - "5435:5432"
    environment:
      - POSTGRES_DB=transaction
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - PGDATA=/var/lib/postgresql/data
    volumes:
      - type: volume
        source: pgsql-transaction
        target: /var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready --username=postgres"]
      interval: 1s
      timeout: 1s
      retries: 30
    networks:
      - smilecdr

  smilecdr:
    restart: "unless-stopped"
    logging:
      driver: "json-file"
      options:
        max-file: "5"
        max-size: "200m"
    image: docker.smilecdr.com/smilecdr:SMILECDR_VERSION
    container_name: smilecdr
    hostname: smilecdr
    volumes:
      - type: bind
        source: ./cdr-config-Master.properties
        target: /home/smile/smilecdr/classes/cdr-config-Master.properties
    ports:
      - "8000:8000"
      - "8001:8001"
      - "8002:8002"
      - "9000:9000"
      - "9100:9100"
      - "9200:9200"
      - "9201:9201"
    depends_on:
      pgsql-clustermgr:
        condition: service_healthy
      pgsql-persistence:
        condition: service_healthy
      pgsql-audit:
        condition: service_healthy
      pgsql-transaction:
        condition: service_healthy
    networks:
      - smilecdr

  nginx:
    restart: always
    image: nginx:stable-alpine
    container_name: nginx
    hostname: nginx
    volumes:
      - type: bind
        source: ~/nginx.conf
        target: /etc/nginx/nginx.conf
      - type: bind
        source: /home/ec2-user/letsencrypt
        target: /etc/letsencrypt
    # volumes:
    #   - ./nginx.conf:/etc/nginx/nginx.conf:ro
    #   - ./letsencrypt:/etc/letsencrypt:ro  # Share certificates with Nginx
    ports:
      - 443:443
    depends_on:
      - smilecdr
      - certbot
    networks:
      - smilecdr

  certbot:
    image: certbot/certbot
    container_name: certbot
    command: certonly --non-interactive --agree-tos --standalone --email email@acme.com -d SMILECDR_DOMAIN
    ports:
      - "80:80"
    environment:
      - CERTBOT_EMAIL=email@acme.com
      - CERTBOT_DOMAIN=SMILECDR_DOMAIN
    volumes:
      - /home/ec2-user/letsencrypt:/etc/letsencrypt  # Persist certificates
      - /home/ec2-user/certbot-logs:/var/log/letsencrypt  # Store logs      

volumes:
  pgsql-clustermgr:
  pgsql-persistence:
  pgsql-audit:
  pgsql-transaction:

networks:
  smilecdr:
    name: smilecdr
    driver: bridge
"""


NGINX_CONFIG = """
user nginx;
worker_processes auto;
pid /var/run/nginx.pid;

events {
    worker_connections  1024;
}

http {
    client_max_body_size 200M;
    server_tokens off;

    server {
        server_name default_server;
        listen 80;

        location / {
            proxy_pass http://smilecdr:9100;
            proxy_http_version 1.1;
            proxy_cache_bypass $http_upgrade;
        }
    
        location /fhir-request {
            proxy_pass http://smilecdr:8000;
            proxy_http_version 1.1;
            proxy_cache_bypass $http_upgrade;
        }
    }

    server {

        listen 443 ssl;
        server_name default_server;

        ssl_certificate /etc/letsencrypt/live/SMILECDR_DOMAIN/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/SMILECDR_DOMAIN/privkey.pem;
        
        location / {
            proxy_pass http://smilecdr:9100;
            proxy_http_version 1.1;
            proxy_cache_bypass $http_upgrade;
        }
    
        location /fhir-request {
            proxy_pass http://smilecdr:8000;
            proxy_http_version 1.1;
            proxy_cache_bypass $http_upgrade;
        }
    }
}
"""


CERTBOT_COMPOSE_YAML = """
services:
  certbot:
    image: certbot/certbot
    container_name: certbot
    command: certonly --non-interactive --agree-tos --standalone \
             --preferred-challenges http \
             --email email@acme.com \
             -d SMILECDR_DOMAIN
    environment:
      - CERTBOT_EMAIL=email@acme.com
      - CERTBOT_DOMAIN=SMILECDR_DOMAIN
    volumes:
      - /home/ec2-user/certs:/etc/letsencrypt  # Persist certificates
      - /home/ec2-user/certbot-logs:/var/log/letsencrypt  # Store logs

services:
  certbot:
    image: certbot/certbot
    container_name: certbot
    command: certonly --non-interactive --agree-tos --standalone --email email@acme.com -d SMILECDR_DOMAIN
    ports:
      - "80:80"
    environment:
      - CERTBOT_EMAIL=email@acme.com
      - CERTBOT_DOMAIN=my-demo02.cloud.relationaldba.com
    volumes:
      - /home/ec2-user/letsencrypt:/etc/letsencrypt  # Persist certificates
      - /home/ec2-user/certbot-logs:/var/log/letsencrypt  # Store logs
"""


AWS_AVAILABILITY_ZONES = {
    "us-east-1": [
        "us-east-1a",
        "us-east-1b",
        "us-east-1c",
        "us-east-1d",
        "us-east-1e",
        "us-east-1f",
    ],
    "us-east-2": ["us-east-2a", "us-east-2b", "us-east-2c"],
    "us-west-1": ["us-west-1a", "us-west-1b", "us-west-1c"],
    "us-west-2": ["us-west-2a", "us-west-2b", "us-west-2c"],
    "ap-south-1": ["ap-south-1a", "ap-south-1b"],
    "ap-northeast-3": ["ap-northeast-3a", "ap-northeast-3b"],
    "ap-northeast-2": ["ap-northeast-2a", "ap-northeast-2b", "ap-northeast-2c"],
    "ap-southeast-1": ["ap-southeast-1a", "ap-southeast-1b"],
    "ap-southeast-2": ["ap-southeast-2a", "ap-southeast-2b"],
    "ap-northeast-1": ["ap-northeast-1a", "ap-northeast-1c"],
    "ca-central-1": ["ca-central-1a", "ca-central-1b"],
    "eu-central-1": ["eu-central-1a", "eu-central-1b", "eu-central-1c"],
}
