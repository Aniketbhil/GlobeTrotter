# GlobeTrotter 🌍

## Personalized Travel Planning Platform

GlobeTrotter is a personalized and interactive travel planning application designed to make multi-city trip planning easier, more organized, and more engaging.

The platform allows users to create and manage customized trips, add multiple destinations, plan activities, estimate expenses, visualize their itinerary, and share their travel plans.

## Problem Statement

Planning a multi-city trip can become complicated when travelers need to manage destinations, dates, activities, budgets, and the overall journey flow in different places.

GlobeTrotter aims to solve this problem by providing a single platform where users can:

- Create customized multi-city itineraries
- Add and manage travel stops and durations
- Explore cities and activities
- Assign travel dates and activities
- Estimate and view trip costs
- Visualize the journey through calendars and timelines
- Share trip plans publicly or with friends

The application should provide a smooth and responsive user experience while storing travel information using a relational database.

## Main Features

### 1. Authentication
- Login
- Signup
- Forgot password
- Basic form validation

### 2. Dashboard
- Welcome section
- Recent trips
- Plan New Trip
- Recommended destinations
- Budget highlights

### 3. Create Trip
Users can create a new trip by entering:
- Trip name
- Start date
- End date
- Trip description
- Optional cover photo

### 4. My Trips
Users can view and manage their existing trips.

Each trip can display:
- Trip name
- Date range
- Number of destinations
- View/Edit/Delete actions

### 5. Itinerary Builder
The core trip-planning area where users can:
- Add destinations/stops
- Select travel dates
- Add activities
- Reorder cities
- Build a day-wise travel plan

### 6. City & Activity Discovery
Users can search for cities and activities and add them to their trips.

### 7. Budget & Cost Breakdown
The application should provide estimated costs for categories such as:
- Transport
- Accommodation
- Activities
- Meals

It can also show the average cost per day and budget alerts.

### 8. Calendar / Timeline
Users can visualize their complete journey using a calendar or timeline view.

### 9. Shared Itinerary
Users can share an itinerary using a public view, allowing others to view or copy the trip.

### 10. Profile & Settings
Users can manage their profile information and preferences.

## Core User Flow

```text
Login / Signup
      ↓
Dashboard
      ↓
Create New Trip
      ↓
Add Cities / Stops
      ↓
Add Activities
      ↓
Arrange Itinerary
      ↓
View Budget
      ↓
Calendar / Timeline
      ↓
Share Trip