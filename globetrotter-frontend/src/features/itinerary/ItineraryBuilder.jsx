import { useParams, Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

export const ItineraryBuilder = () => {
  const { tripId } = useParams();

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-in fade-in duration-500">
      <Link to="/dashboard" className="inline-flex items-center text-sm font-medium text-text-secondary hover:text-primary transition-colors">
        <ArrowLeft size={16} className="mr-2" />
        Back to Dashboard
      </Link>
      <h1 className="text-3xl font-bold font-manrope text-text-primary">Itinerary Builder</h1>
      <p className="text-text-secondary mt-1">Trip ID: {tripId}</p>
      
      <div className="p-12 text-center bg-surface border border-dashed border-border-strong rounded-2xl">
        <p className="text-text-muted">In the next chapter, we will add stops, activities, and budget planning here!</p>
      </div>
    </div>
  );
};