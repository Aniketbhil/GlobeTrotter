import { useEffect, useState, useCallback } from 'react';
import { ChevronLeft, ChevronRight, MapPin } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { getMonthCalendar } from './calendarApi';

export const CalendarView = () => {
  const currentDate = new Date();
  const [currentYear, setCurrentYear] = useState(currentDate.getFullYear());
  const [currentMonth, setCurrentMonth] = useState(currentDate.getMonth() + 1); // 1-12
  const [calendarData, setCalendarData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchCalendar = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await getMonthCalendar(currentYear, currentMonth);
      setCalendarData(data);
    } catch (error) {
      console.error("Failed to load calendar", error);
    } finally {
      setIsLoading(false);
    }
  }, [currentYear, currentMonth]);

  useEffect(() => {
    fetchCalendar();
  }, [fetchCalendar]);

  const handlePrevMonth = () => {
    if (currentMonth === 1) {
      setCurrentMonth(12);
      setCurrentYear((prev) => prev - 1);
    } else {
      setCurrentMonth((prev) => prev - 1);
    }
  };

  const handleNextMonth = () => {
    if (currentMonth === 12) {
      setCurrentMonth(1);
      setCurrentYear((prev) => prev + 1);
    } else {
      setCurrentMonth((prev) => prev + 1);
    }
  };

  // Calendar Grid Logic
  const getDaysInMonth = (year, month) => new Date(year, month, 0).getDate();
  const getFirstDayOfMonth = (year, month) => new Date(year, month - 1, 1).getDay(); // 0 = Sun, 1 = Mon...

  const daysInMonth = getDaysInMonth(currentYear, currentMonth);
  const firstDay = getFirstDayOfMonth(currentYear, currentMonth);
  
  const blanks = Array.from({ length: firstDay }, (_, i) => i);
  const days = Array.from({ length: daysInMonth }, (_, i) => i + 1);

  const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

  // Helper to check if a trip falls on a specific date
  const getTripsForDay = (day) => {
    if (!calendarData || !calendarData.trips) return [];
    const currentDateStr = `${currentYear}-${String(currentMonth).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    const checkDate = new Date(currentDateStr);
    
    return calendarData.trips.filter(trip => {
      const start = new Date(trip.start_date);
      const end = new Date(trip.end_date);
      // Normalize times for accurate date comparison
      start.setHours(0,0,0,0);
      end.setHours(23,59,59,999);
      return checkDate >= start && checkDate <= end;
    });
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'ongoing': return 'bg-warning text-warning-contrast';
      case 'completed': return 'bg-success text-success-contrast';
      default: return 'bg-primary text-text-on-primary';
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-in fade-in duration-500 pb-16">
      
      {/* Header Matching Screen 11 */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div>
          <h1 className="text-3xl font-bold font-manrope text-text-primary">Calendar View</h1>
          <p className="text-text-secondary mt-1">Visualize your upcoming travel schedule.</p>
        </div>
        
        <div className="flex items-center gap-4 bg-surface p-2 rounded-xl border border-border-default shadow-sm">
          <Button variant="ghost" onClick={handlePrevMonth} className="px-2">
            <ChevronLeft size={20} />
          </Button>
          <span className="w-32 text-center font-bold text-text-primary">
            {monthNames[currentMonth - 1]} {currentYear}
          </span>
          <Button variant="ghost" onClick={handleNextMonth} className="px-2">
            <ChevronRight size={20} />
          </Button>
        </div>
      </div>

      <div className="mt-2">
        {/* Days of week header */}
        <div className="grid grid-cols-7 mb-2">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
            <div key={day} className="p-2 text-center text-sm font-bold text-text-secondary uppercase tracking-wider">
              {day}
            </div>
          ))}
        </div>

        {/* Calendar Grid */}
        <div className="grid grid-cols-7 gap-2 sm:gap-3">
          {isLoading ? (
            <div className="col-span-7 p-20 text-center text-text-muted animate-pulse bg-surface rounded-2xl border border-border-subtle">
              Loading calendar data...
            </div>
          ) : (
            <>
              {/* Empty padding for start of month */}
              {blanks.map(blank => (
                <div key={`blank-${blank}`} className="min-h-[120px] p-2"></div>
              ))}
              
              {/* Actual Days */}
              {days.map(day => {
                const dayTrips = getTripsForDay(day);
                const isToday = day === currentDate.getDate() && currentMonth === (currentDate.getMonth() + 1) && currentYear === currentDate.getFullYear();
                
                return (
                  <div key={day} className={`min-h-[120px] p-2 sm:p-3 transition-colors rounded-2xl border border-border-subtle hover:border-primary/30 hover:shadow-sm ${isToday ? 'ring-2 ring-primary/50 bg-primary-soft/20' : 'bg-surface'}`}>
                    <div className="flex justify-between items-start mb-2">
                      <span className={`text-sm font-semibold w-7 h-7 flex items-center justify-center rounded-full ${isToday ? 'bg-primary text-text-on-primary shadow-sm' : 'text-text-primary'}`}>
                        {day}
                      </span>
                    </div>
                    
                    {/* Trip Bars */}
                    <div className="space-y-1.5">
                      {dayTrips.map(trip => (
                        <Link key={trip.trip_id} to={`/trips/${trip.trip_id}/itinerary`} className="block">
                          <div className={`px-2 py-1.5 rounded-md text-[10px] uppercase font-bold truncate shadow-sm transition-transform hover:scale-[1.02] ${getStatusColor(trip.status)}`}>
                            {trip.name}
                          </div>
                        </Link>
                      ))}
                    </div>
                  </div>
                );
              })}
            </>
          )}
        </div>
      </div>
    </div>
  );
};