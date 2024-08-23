from amadeus import Client, ResponseError, Location
import time
from django.http import JsonResponse
import json
import requests

quotas = {
    "flight_offers_search": 2000, 
    "flight_offers_price": 3000, 
    "flight_orders": 10000,
    "seatmaps": 1000,
    "branded_fairs_upsell": 3000, 
    "flight_price_analysis": 10000, 
    "flight_inspiration_search": 3000, 
    "flight_cheapest_date_search": 3000, 
    "flight_avaliabilites_search": 3000, 
    "travel_reccomendations": 10000, 
    "on_demand_flight_status": 2000, 
    "points_of_interest": 400,
    "points_of_interest_by_square": 400, 
    "shopping_activities": 400,
    "shopping_by_square": 400,
    "city_search": 3000, 

}

amadeus = Client(client_id='u6bpzmGFnxEJ18MR6wRi69cj8aPEZ6OG', client_secret='qXqQGbWkNvB4me6H')
accessTokenForCurrentClient = 'sCazHEK0uQ18AI395nFuC6RhTBoD'


def flight_offers_search(**kwargs):
    '''
    API lets you search flights between two cities, perform multi-city searches for longer itineraries and access one-way combinable fares to offer the cheapest options possible. 
    For each itinerary, the API provides a list of flight offers with prices, fare details, airline names, baggage allowances and departure terminals. 
    '''
    context = {"data": []}
    try:
        params = {key: value for key, value in kwargs.items() if value is not None}
        
        response = amadeus.shopping.flight_offers_search.get(**params)
        
        context["data"].extend(response.data)
        
        return json.dumps(context, indent=2)
    
    except ResponseError as error:
        return "Error occurred while fetching flight offers. Please ensure that all the required fields are filled out correctly."
    

def flight_offers_price(**kwargs):
    return ''


def branded_fares(**kwargs):
    '''
    Branded fares, or fare families, are airline-created fares that combine different products and services like bags, sets, meals, free cancellation or miles accrual. 
    '''
    context = {"data": []}
    try:
        params = {key: value for key, value in kwargs.items() if value is not None}
        
        response = amadeus.shopping.flight_offers.upselling.post(**params)
        
        context["data"].extend(response.data)
        
        return json.dumps(context, indent=2)
    
    except ResponseError as error:
        return "Error occurred while trying to find branded fares for the given airline. Please ensure that all the required fields are filled out correctly."
    

def flight_price_analysis(**kwargs):
    '''
    Artificial Intelligence algorithm trained on Amadeus historical flight booking data to show how current flight prices compare to historical fares and whether the price of a flight is below or above average. .
    Prices are based on Amadeus flight booking data from 2019
    '''
    context = {"data": []}
    try:
        params = {key: value for key, value in kwargs.items() if value is not None}
        
        response = amadeus.analytics.itinerary_price_metrics.get(**params)
        
        context["data"].extend(response.data)
        
        return json.dumps(context, indent=2)
    
    except ResponseError as error:
        return "Error occurred while trying to predict whether the given deal is in your best interest. Please ensure that all the required fields are filled out correctly."
    
    
def on_demand_flight_status(**kwargs):
    '''
    Real-time flight schedule data including up-to-date departure and arrival times, terminal and gate information, flight duration and real-time delay status.
    '''
    context = {"data": []}
    try:
        params = {key: value for key, value in kwargs.items() if value is not None}
        
        response = amadeus.schedule.flights.get(**params)
        
        context["data"].extend(response.data)
        
        return json.dumps(context, indent=2)
    
    except ResponseError as error:
        return "Error occurred while fetching flight status. Please ensure that all the required fields are filled out correctly."


def flight_delay_pred(**kwargs):
    '''
    Meant to predict whether the flight will be delayed months prior to takeoff.
    '''
    context = {"data": []}
    try:
        params = {key: value for key, value in kwargs.items() if value is not None}
        
        response = amadeus.travel.predictions.flight_delay.get(**params)
        
        context["data"].extend(response.data)
        
        return json.dumps(context, indent=2)
    
    except ResponseError as error:
        return "Error occurred while trying to predict whether the given flight will be delayed. Please ensure that all the required fields are filled out correctly."
    

def travel_recommendations(**kwargs):
    '''
    Provides travelers personalized destination recommendations based on their location and an input destination, such as a previously searched flight destination or city of interest. 
    The API uses Artificial Intelligence trained on Amadeus historical flight search data to determine which destinations are also popular among travelers with similar profiles, and provides a list of recommended destinations with name, IATA code, coordinates and similarity score.
    '''
    context = {"data": []}
    try:
        params = {key: value for key, value in kwargs.items() if value is not None}
        
        response = amadeus.reference_data.recommended_locations.get(**params)
        
        context["data"].extend(response.data)
        
        return json.dumps(context, indent=2)
    
    except ResponseError as error:
        return "Error occurred while trying to find travel recommendations. Please ensure that all the required fields are filled out correctly."
    

def nearest_airport(**kwargs):
    '''
    Meant to find the nearest airport within a 500km radius. 
    '''
    context = {"data": []}
    try:
        params = {key: value for key, value in kwargs.items() if value is not None}
        
        response = amadeus.reference_data.locations.airports.get(**params)
        
        context["data"].extend(response.data)
        
        return json.dumps(context, indent=2)
    
    except ResponseError as error:
        return "Error occurred while trying to find the nearest airport within a 500km radius. Please ensure that all the required fields are filled out correctly."


def transfer_search(**kwargs):
    '''
    Meant to find forms of transportation.
    '''
    context = {"data": []}
    try:
        params = {key: value for key, value in kwargs.items() if value is not None}
        
        response = amadeus.shopping.transfer_offers.post(**params)
        
        context["data"].extend(response.data)
        
        return json.dumps(context, indent=2)
    
    except ResponseError as error:
        return "Error occurred while trying to find transportation. Please ensure that all the required fields are filled out correctly."


def hotel_by_city(**kwargs):
    '''
    Meant to find hotels within the given city.
    '''
    context = {"data": []}
    try:
        params = {key: value for key, value in kwargs.items() if value is not None}
        response = amadeus.reference_data.locations.hotels.by_city.get(**params)
        context["data"].extend(response.data)
        return json.dumps(context, indent=2)
    except ResponseError as error:
        raise "Error occurred while trying to find hotels within the given city. Please ensure that all the required fields are filled out correctly."
    

def hotel_by_geolocation(**kwargs):
    '''
    Meant to find hotels with a city by the given coordinates.
    '''
    context = {"data": []}
    try:
        params = {key: value for key, value in kwargs.items() if value is not None}
        response = amadeus.reference_data.locations.hotels.by_geocode.get(**params)
        context["data"].extend(response.data)
        return json.dumps(context, indent=2)
    except ResponseError as error:
        raise "Error occurred while trying to find hotels within the city represented by the given coordinates. Please ensure that all the required fields are filled out correctly."
    

def hotel_rating_by_id(**kwargs):
    '''
    Meant to find the rating of a hotel using its id.
    '''
    context = {"data": []}
    try:
        params = {key: value for key, value in kwargs.items() if value is not None}
        response = amadeus.e_reputation.hotel_sentiments.get(**params)
        context["data"].extend(response.data)
        return json.dumps(context, indent=2)
    except ResponseError as error:
        raise "Error occurred while trying to find hotel rating. Please ensure that all the required fields are filled out correctly."


def hotel_name_autocomplete(**kwargs):
    '''
    Meant to find the rating of a hotel using its id.
    '''
    context = {"data": []}
    try:
        params = {key: value for key, value in kwargs.items() if value is not None}
        response = amadeus.reference_data.locations.hotel.get(**params)
        context["data"].extend(response.data)
        return json.dumps(context, indent=2)
    except ResponseError as error:
        raise "Error occurred while trying to find hotel rating. Please ensure that all the required fields are filled out correctly."


'''
flight_offers = flight_offers_search(
    originLocationCode=None,
    destinationLocationCode=None,
    departureDate=None,
    returnDate=None,
    adults=None,
    travelClass=None,
    currencyCode=None
)
print(flight_offers)

flight_status = on_demand_flight_status(
    carrierCode='LH',
    flightNumber='400',
    scheduledDepartureDate='2024-08-01'
)
print(flight_status)
'''
print(hotel_by_city(cityCode='PAR'))