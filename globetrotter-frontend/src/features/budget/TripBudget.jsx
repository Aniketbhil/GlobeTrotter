import { useEffect, useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Wallet, TrendingUp, AlertCircle, Plane, Bed, Activity, Utensils } from 'lucide-react';
import { Card, CardContent } from '../../components/ui/Card';
import { getTripBudget } from './budgetApi';

export const TripBudget = () => {
  const { tripId } = useParams();
  const [budget, setBudget] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchBudget = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await getTripBudget(tripId);
      setBudget(data);
    } catch (error) {
      console.error("Failed to load budget", error);
    } finally {
      setIsLoading(false);
    }
  }, [tripId]);

  useEffect(() => {
    fetchBudget();
  }, [fetchBudget]);

  if (isLoading) return <div className="p-12 text-center text-text-muted animate-pulse">Calculating expenses...</div>;
  if (!budget) return <div className="p-12 text-center text-error">Failed to load budget data.</div>;

  const { category_totals, trip_total_cost, overbudget_day_count } = budget;

  // Calculate percentages for visual bars
  const getPercentage = (amount) => trip_total_cost > 0 ? Math.round((amount / trip_total_cost) * 100) : 0;

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in duration-500 pb-16">
      
      <Link to={`/trips/${tripId}/itinerary`} className="inline-flex items-center text-sm font-medium text-text-secondary hover:text-primary transition-colors">
        <ArrowLeft size={16} className="mr-2" /> Back to Itinerary
      </Link>
      
      <div className="mb-6">
        <h1 className="text-3xl font-bold font-manrope text-text-primary">{budget.trip_name} - Budget</h1>
        <p className="text-text-secondary mt-1">Review your estimated costs and financial breakdown.</p>
      </div>

      {/* Top KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="bg-surface border-border-default shadow-sm">
          <CardContent className="p-6 flex items-center gap-4">
            <div className="w-14 h-14 bg-primary-soft text-primary rounded-full flex items-center justify-center shrink-0">
              <Wallet size={28} />
            </div>
            <div>
              <p className="text-sm font-semibold text-text-secondary uppercase tracking-wider">Estimated Total</p>
              <p className="text-3xl font-bold text-text-primary mt-1">${trip_total_cost.toLocaleString()}</p>
            </div>
          </CardContent>
        </Card>

        <Card className={`border shadow-sm ${overbudget_day_count > 0 ? 'bg-error-soft border-error/30' : 'bg-success-soft border-success/30'}`}>
          <CardContent className="p-6 flex items-center gap-4">
            <div className={`w-14 h-14 rounded-full flex items-center justify-center shrink-0 ${overbudget_day_count > 0 ? 'bg-error/20 text-error' : 'bg-success/20 text-success'}`}>
              {overbudget_day_count > 0 ? <AlertCircle size={28} /> : <TrendingUp size={28} />}
            </div>
            <div>
              <p className="text-sm font-semibold uppercase tracking-wider opacity-80">Budget Status</p>
              <p className="text-xl font-bold mt-1">
                {overbudget_day_count > 0 ? `${overbudget_day_count} Days Overbudget` : 'On Track'}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Category Breakdown */}
      <h2 className="text-xl font-bold font-manrope text-text-primary mt-8 mb-4">Cost Breakdown</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <CategoryCard title="Transport" amount={category_totals.transport} percent={getPercentage(category_totals.transport)} icon={Plane} colorClass="text-primary bg-primary" bgSoftClass="bg-primary-soft" />
        <CategoryCard title="Stay" amount={category_totals.stay} percent={getPercentage(category_totals.stay)} icon={Bed} colorClass="text-info bg-info" bgSoftClass="bg-info-soft" />
        <CategoryCard title="Activities" amount={category_totals.activities} percent={getPercentage(category_totals.activities)} icon={Activity} colorClass="text-accent bg-accent" bgSoftClass="bg-accent-soft" />
        <CategoryCard title="Meals" amount={category_totals.meals} percent={getPercentage(category_totals.meals)} icon={Utensils} colorClass="text-success bg-success" bgSoftClass="bg-success-soft" />
      </div>

      {/* Destination Breakdown Cards */}
      {budget.stops.length > 0 && (
        <>
          <h2 className="text-xl font-bold font-manrope text-text-primary mt-8 mb-4">By Destination</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {budget.stops.map(stop => (
              <Card key={stop.stop_id} className="bg-surface hover:border-primary/50 transition-colors shadow-sm">
                <CardContent className="p-5">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-lg font-bold text-text-primary font-manrope">{stop.city?.name}</h3>
                      <p className="text-sm text-text-secondary mt-0.5">{stop.nights} Nights</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1">Total</p>
                      <p className="text-2xl font-bold text-primary">${stop.stop_total}</p>
                    </div>
                  </div>
                  <div className="flex gap-6 border-t border-border-subtle pt-3 mt-1">
                    <div className="flex items-center gap-2">
                      <div className="p-1.5 bg-info-soft text-info rounded-md">
                        <Bed size={14} />
                      </div>
                      <div>
                        <p className="text-xs text-text-muted">Stay</p>
                        <p className="text-sm font-semibold text-text-primary">${stop.stay_cost}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="p-1.5 bg-accent-soft text-accent rounded-md">
                        <Activity size={14} />
                      </div>
                      <div>
                        <p className="text-xs text-text-muted">Activities</p>
                        <p className="text-sm font-semibold text-text-primary">${stop.activity_cost}</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

// Sub-component for visual category bars
const CategoryCard = ({ title, amount, percent, icon: Icon, colorClass, bgSoftClass }) => (
  <Card>
    <CardContent className="p-5">
      <div className="flex justify-between items-center mb-3">
        <div className="flex items-center gap-2">
          <div className={`p-2 rounded-lg ${bgSoftClass} ${colorClass.split(' ')[0]}`}>
            <Icon size={16} />
          </div>
          <span className="font-semibold text-text-primary">{title}</span>
        </div>
        <span className="font-bold text-text-primary">${amount.toLocaleString()}</span>
      </div>
      <div className="w-full bg-surface-muted rounded-full h-2.5 overflow-hidden">
        <div className={`h-2.5 rounded-full ${colorClass.split(' ')[1]}`} style={{ width: `${percent}%` }}></div>
      </div>
      <p className="text-xs text-text-muted mt-2 text-right">{percent}% of total</p>
    </CardContent>
  </Card>
);