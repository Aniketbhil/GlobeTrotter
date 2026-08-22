import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { MapPin, Calendar, Clock, Copy, ArrowRight } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Card, CardContent } from '../../components/ui/Card';
import { getPublicItinerary, copyTrip } from './sharingApi';
import { useAuthStore } from '../../store/authStore';
import logo from '../../assets/GlobeTrotter_Logo.png';

export const PublicItinerary = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { token } = useAuthStore(); // Check if user is logged in
  
  const [itinerary, setItinerary] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCopying, setIsCopying] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchPublicData = async () => {
      try {
        const data = await getPublicItinerary(slug);
        setItinerary(data);
      } catch (err) {
        setError("This trip does not exist or is no longer public.");
      } finally {
        setIsLoading(false);
      }
    };
    fetchPublicData();
  }, [slug]);

  const handleCopyTrip = async () => {
    if (!token) {
      // Prompt them to login, passing current URL so they can return
      navigate('/login', { state: { message: "Please log in or create an account to copy this trip!" } });
      return;
    }

    setIsCopying(true);
    try {
      const clonedTrip = await copyTrip(slug);
      navigate(`/trips/${clonedTrip.id}/itinerary`);
    } catch (err) {
      alert("Failed to copy trip.");
      setIsCopying(false);
    }
  };

  if (isLoading) return <div className="min-h-screen flex items-center justify-center bg-background"><div className="animate-pulse">Loading itinerary...</div></div>;
  
  if (error || !itinerary) return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background p-4">
      <img src={logo} alt="GlobeTrotter" className="h-10 mb-6 opacity-50" />
      <p className="text-error font-medium">{error}</p>
      <Link to="/"><Button className="mt-4">Go Home</Button></Link>
    </div>
  );

  return (
    <div className="min-h-screen bg-background">
      {/* Public Top Navbar */}
      <div className="bg-surface border-b border-border-default sticky top-0 z-20 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <img src={logo} alt="GlobeTrotter" className="h-8 w-auto" onError={(e) => { e.target.style.display = 'none'; }} />
          <Button onClick={handleCopyTrip} isLoading={isCopying} className="gap-2">
            {token ? <Copy size={16} /> : <ArrowRight size={16} />}
            {token ? "Copy to My Account" : "Login to Copy"}
          </Button>
        </div>
      </div>

      <div className="max-w-4xl mx-auto p-4 sm:p-6 lg:p-8 space-y-8 animate-in fade-in duration-500">
        
        {/* Cover Photo & Header */}
        <div className="relative rounded-3xl overflow-hidden bg-surface-muted h-64 border border-border-default shadow-sm flex flex-col justify-end p-8">
          {itinerary.cover_photo_url && (
            <img src={itinerary.cover_photo_url} alt={itinerary.trip_name} className="absolute inset-0 w-full h-full object-cover" />
          )}
          <div className="absolute inset-0 bg-linear-to-t from-black/80 via-black/30 to-transparent" />
          <div className="relative z-10 text-white">
            <span className="inline-block px-3 py-1 bg-primary/20 backdrop-blur-md rounded-full text-xs font-semibold uppercase tracking-wider mb-3 text-white border border-white/20">
              Shared Itinerary
            </span>
            <h1 className="text-4xl font-bold font-manrope">{itinerary.trip_name}</h1>
            <div className="flex items-center gap-2 mt-2 text-sm font-medium text-white/90">
              <Calendar size={16} />
              <span>{new Date(itinerary.start_date).toLocaleDateString()} - {new Date(itinerary.end_date).toLocaleDateString()}</span>
            </div>
          </div>
        </div>

        {/* Read-Only Timeline */}
        <div className="space-y-6 relative before:absolute before:inset-0 before:ml-6 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-border-default before:hidden md:before:block">
          {itinerary.stops?.map((stop, index) => (
            <div key={index} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group">
              
              <div className="hidden md:flex items-center justify-center w-12 h-12 rounded-full border-4 border-background bg-surface-muted text-text-muted shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
                <MapPin size={20} />
              </div>

              <Card className="w-full md:w-[calc(50%-2.5rem)]">
                <CardContent className="p-5">
                  <div className="mb-4">
                    <span className="text-xs font-bold text-text-muted uppercase tracking-wider">Destination {index + 1}</span>
                    <h3 className="text-xl font-bold font-manrope text-text-primary mt-1">{stop.city?.name}, {stop.city?.country}</h3>
                    <p className="text-sm font-medium text-text-secondary mt-1">
                      {new Date(stop.start_date).toLocaleDateString()} - {new Date(stop.end_date).toLocaleDateString()}
                    </p>
                  </div>
                  
                  {stop.activities && stop.activities.length > 0 ? (
                    <div className="space-y-2 pt-4 border-t border-border-subtle">
                      {stop.activities.map((act, actIndex) => (
                        <div key={actIndex} className="flex items-center gap-3 bg-surface-hover p-3 rounded-xl border border-border-subtle">
                          {act.image_url ? (
                             <img src={act.image_url} alt="" className="w-10 h-10 rounded-lg object-cover shrink-0" />
                          ) : (
                            <div className="w-10 h-10 bg-primary-soft text-primary rounded-lg flex items-center justify-center shrink-0">
                              <Clock size={16} />
                            </div>
                          )}
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-semibold text-text-primary truncate">{act.name}</p>
                            <p className="text-xs text-text-secondary">{act.type} • {act.duration_mins} min</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-text-muted italic pt-4 border-t border-border-subtle">No specific activities planned.</p>
                  )}
                </CardContent>
              </Card>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
};