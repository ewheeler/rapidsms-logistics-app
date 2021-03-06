#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import datetime

from django.db import models

from rapidsms.models import ExtensibleModelBase
from rapidsms.models import Contact
from rapidsms.contrib.locations.models import Location


class CommodityBase(models.Model):
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
        ('UK', 'Unknown'),
    )
    name = models.CharField(max_length=160)
    slug = models.CharField(max_length=20, unique=True)
    # List of alternate spellings, abbreviations, etc that can be specified
    # via webui. eg, enter books, book for object where slug=textbooks
    aliases = models.CharField(max_length=160, blank=True, null=True,\
        help_text="List of alternate spellings, abbreviations, etc. Separate each alias with a single comma and no spaces.")

    # unit of commodity for shipping purposes
    unit = models.CharField(max_length=3, choices=UNIT_CHOICES)

    # per unit shipping volume and weight of commodity
    volume = models.CharField(max_length=160, blank=True, null=True)
    weight = models.CharField(max_length=160, blank=True, null=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name

    def alias_list(self):
        ''' Returns a list of self.aliases '''
        if self.aliases is not None:
            return self.aliases.split(',')
        else:
            return None

    def has_alias(self, term):
        ''' Checks whether a search term is in a commodity's list
            of aliases. Returns None if commodity has no aliases,
            and True or False otherwise. '''
        if self.aliases is not None:
            alias_list = self.alias_list()
            if term in alias_list:
                return True
            else:
                return False
        else:
            return None

class Commodity(CommodityBase):
    ''' Stuff '''
    __metaclass__ = ExtensibleModelBase

class CargoBase(models.Model):
    commodity = models.ForeignKey(Commodity)
    quantity = models.CharField(max_length=160)

    class Meta:
        abstract = True

    def __unicode__(self):
        return "%s %s of %s" % (self.quantity, self.commodity.get_unit_display(), self.commodity.slug)

class Cargo(CargoBase):
    ''' An amount of stuff being transported '''
    __metaclass__ = ExtensibleModelBase

class ShipmentBase(models.Model):
    STATUS_CHOICES = (
        ('P', 'Planned shipment'),
        ('T', 'Shipment in transit'),
        ('D', 'Shipment delivered'),
    )
    status = models.CharField(max_length=3, choices=STATUS_CHOICES)
    cargos = models.ManyToManyField(Cargo)

    origin = models.ForeignKey(Location, related_name='origin', blank=True, null=True)
    destination = models.ForeignKey(Location, related_name='destination')

    created = models.DateTimeField(default=datetime.datetime.utcnow)
    modified = models.DateTimeField(default=datetime.datetime.utcnow)

    # datetime when transport begins
    shipping_time = models.DateTimeField(blank=True, null=True)
    # estimated delivery datetime
    expected_delivery_time = models.DateTimeField(blank=True, null=True)
    # actual datetime of shipment delivery
    # TODO derive from a ShipmentSighting at destination?
    actual_delivery_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        cargos_names = []
        for cargo in self.cargos.all():
            if cargo.commodity.slug not in cargos_names:
                cargos_names.append(cargo.commodity.slug)
        if self.origin is not None:
            return "%s from %s to %s" % (", ".join(cargos_names), self.origin.name, self.destination.name)
        else:
            return "%s from ?? to %s" % (", ".join(cargos_names), self.destination.name)

    @classmethod
    def active(cls):
        return cls.objects.exclude(status="D")

class Shipment(ShipmentBase):
    ''' Transport of stuff(s) between two places '''
    __metaclass__ = ExtensibleModelBase

class ShipmentSightingBase(models.Model):
    updated = models.DateTimeField(default=datetime.datetime.utcnow)
    location = models.ForeignKey(Location)
    observed_cargo = models.ForeignKey(Cargo, blank=True, null=True)
    seen_by = models.ForeignKey(Contact)

    class Meta:
        abstract = True

    def __unicode__(self):
        return "%s seen by %s at %s" % (self.observed_cargo, self.seen_by.name, self.location.name)

class ShipmentSighting(ShipmentSightingBase):
    ''' Location where a person has seen stuff during its shipment '''
    __metaclass__ = ExtensibleModelBase

class ShipmentRouteBase(models.Model):
    shipment = models.ForeignKey(Shipment)
    sightings = models.ManyToManyField(ShipmentSighting)

    class Meta:
        abstract = True

    def __unicode__(self):
        return "%s sightings of %s" % (self.sightings.count(), self.shipment)

class ShipmentRoute(ShipmentRouteBase):
    ''' Collection of locations where the stuff has been seen during shipment '''
    __metaclass__ = ExtensibleModelBase
