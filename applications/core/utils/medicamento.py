from django.db import models

class ViaAdministracion(models.TextChoices):
    ORAL = "oral", "Oral"
    SUBLINGUAL = "sublingual", "Sublingual"
    TOPICA = "topica", "Tópica"
    INHALATORIA = "inhalatoria", "Inhalatoria"
    INTRAVENOSA = "intravenosa", "Intravenosa"
    INTRAMUSCULAR = "intramuscular", "Intramuscular"
    SUBCUTANEA = "subcutanea", "Subcutánea"
    INTRATECAL = "intratecal", "Intratecal"
    INTRAARTICULAR = "intraarticular", "Intraarticular"
    RECTAL = "rectal", "Rectal"
    VAGINAL = "vaginal", "Vaginal"
    OFTALMICA = "oftalmica", "Oftálmica"
    OTIC = "otic", "Ótica"
    NASAL = "nasal", "Nasal"
    OTRA = "otra", "Otra"