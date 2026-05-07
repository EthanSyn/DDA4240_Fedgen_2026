##############################################################
# FedGen Data Backend - serves sample datasets via HTTP
# Accessible inside k8s as http://fedgen-data-backend:8080
##############################################################

resource "kubernetes_config_map" "fedgen_data" {
  metadata {
    name      = "fedgen-data"
    namespace = var.namespace
  }
  data = {
    "legal_sample.json" = file("${path.module}/../data/legal_sample.json")
    "news_sample.json"  = file("${path.module}/../data/news_sample.json")
  }
}

resource "kubernetes_config_map" "fedgen_backend_code" {
  metadata {
    name      = "fedgen-backend-code"
    namespace = var.namespace
  }
  data = {
    "server.py" = file("${path.module}/../data-backend/server.py")
  }
}

resource "kubernetes_deployment" "fedgen_data_backend" {
  metadata {
    name      = "fedgen-data-backend"
    namespace = var.namespace
    labels = { App = "fedgen-data-backend" }
  }
  spec {
    replicas = 1
    selector { match_labels = { App = "fedgen-data-backend" } }
    template {
      metadata { labels = { App = "fedgen-data-backend" } }
      spec {
        container {
          name  = "data-backend"
          image = "python:3.12-alpine"
          command = ["python", "/app/server.py"]
          port {
            container_port = 8080
          }
          env {
            name  = "DATA_DIR"
            value = "/data"
          }
          env {
            name  = "PORT"
            value = "8080"
          }
          volume_mount {
            name       = "data"
            mount_path = "/data"
          }
          volume_mount {
            name       = "code"
            mount_path = "/app"
          }
          liveness_probe {
            http_get {
              path = "/health"
              port = 8080
            }
            initial_delay_seconds = 5
            period_seconds        = 30
          }
        }
        volume {
          name = "data"
          config_map { name = kubernetes_config_map.fedgen_data.metadata[0].name }
        }
        volume {
          name = "code"
          config_map { name = kubernetes_config_map.fedgen_backend_code.metadata[0].name }
        }
      }
    }
  }
}

resource "kubernetes_service" "fedgen_data_backend" {
  metadata {
    name      = "fedgen-data-backend"
    namespace = var.namespace
  }
  spec {
    selector = { App = "fedgen-data-backend" }
    port {
      port        = 8080
      target_port = 8080
    }
  }
}

variable "namespace" {
  type    = string
  default = "mvd"
}
