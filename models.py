#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import datetime

from django.db import models

from rapidsms.models import Contact
from rapidsms.contrib.locations.models import Location


class Commodity(models.Model):
    ''' Stuff '''
    UNIT_CHOICES = (
        ('PL', 'pallets'),
        ('TM', 'Tons (metric)'),
        ('KG', 'Kilograms'),
        ('BX', 'Boxes'),
        ('TB', 'Tiny boxes'),
        ('BL', 'Bales'),
        ('LT', 'Liters'),
        ('CN', 'Containers'),
        ('DS', 'Doses'),
    )
    name = models.CharField(max_length=160)
    slug = models.CharField(max_length=6, unique=True)

    # unit of commodity for shipping purposes
    unit = models.CharField(max_length=2, choices=UNIT_CHOICES)

    # per unit shipping volume and weight of commodity
    volume = models.CharField(max_length=160)
    weight = models.CharField(max_length=160)

    def __unicode__(self):
        return self.name

class Cargo(models.Model):
    ''' An amount of stuff being transported '''
    commodity = models.ForeignKey(Commodity)
    quantity = models.CharField(max_length=160)

    def __unicode__(self):
        return "%s pallets of %s to %s" % (self.quantity, self.commodity, self.shipment.destination)

class Shipment(models.Model):
    ''' Transport of stuff(s) between two places '''
    STATUS_CHOICES = (
        ('P', 'Planned shipment'),
        ('T', 'Shipment in transit'),
        ('D', 'Shipment delivered'),
    )
    status = models.CharField(max_length=2, choices=STATUS_CHOICES)
    cargo = models.ManyToManyField(Cargo)

    origin = models.ForeignKey(Location, related_name='origin')
    destination = models.ForeignKey(Location, related_name='destination')

    created = models.DateTimeField(default=datetime.datetime.utcnow)
    modified = models.DateTimeField(default=datetime.datetime.utcnow)

    # datetime when transport begins
    shipping_time = models.DateTimeField()
    # estimated delivery datetime
    expected_delivery_time = models.DateTimeField()
    # actual datetime of shipment delivery
    # TODO derive from a ShipmentSighting at destination?
    actual_delivery_time = models.DateTimeField()

    def __unicode__(self):
        return "Shipment of %s pallets of %s to %s" % (self.cargo.quantity, self.cargo.commodity, self.destination)

    class Meta:
        verbose_name = "Shipment"

    @classmethod
    def active(cls):
        return cls.objects.exclude(status="D")

class ShipmentSighting(models.Model):
    ''' Location where a person has seen stuff during its shipment '''
    updated = models.DateTimeField(default=datetime.datetime.utcnow)
    location = models.ForeignKey(Location)
    seen_by = models.ForeignKey(Contact)

class ShipmentRoute(models.Model):
    ''' Collection of locations where the stuff has been seen during shipment '''
    shipment = models.ForeignKey(Shipment)
    sightings = models.ManyToManyField(ShipmentSighting)
