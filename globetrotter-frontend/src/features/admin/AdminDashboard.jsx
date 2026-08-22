import { useEffect, useState } from 'react';
import { Users, Map, Activity, TrendingUp, Search } from 'lucide-react';
import { Card, CardContent } from '../../components/ui/Card';
import { Input } from '../../components/ui/Input';
import { Badge } from '../../components/ui/Badge';
import { getStatsOverview, getTopCities, getTopActivities, getUsers } from './adminApi';

export const AdminDashboard = () => {
  const [overview, setOverview] = useState(null);
  const [cities, setCities] = useState([]);
  const [activities, setActivities] = useState([]);
  const [usersData, setUsersData] = useState({ items: [], total: 0 });
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    setIsLoading(true);
    try {
      const [overviewData, citiesData, activitiesData, usersList] = await Promise.all([
        getStatsOverview(),
        getTopCities(5),
        getTopActivities(5),
        getUsers()
      ]);
      setOverview(overviewData);
      setCities(citiesData);
      setActivities(activitiesData);
      setUsersData(usersList);
    } catch (error) {
      console.error("Failed to load admin stats", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearchUsers = async (e) => {
    e.preventDefault();
    try {
      const usersList = await getUsers(searchQuery);
      setUsersData(usersList);
    } catch (error) {
      console.error("Failed to search users");
    }
  };

  if (isLoading) return <div className="p-12 text-center text-text-muted animate-pulse">Loading analytics...</div>;
  if (!overview) return <div className="p-12 text-center text-error">Failed to load admin dashboard.</div>;

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in duration-500 pb-16">
      
      <div className="mb-6">
        <h1 className="text-3xl font-bold font-manrope text-text-primary">Admin Analytics</h1>
        <p className="text-text-secondary mt-1">Platform overview and user trends.</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard title="Total Users" value={overview.total_users} icon={Users} colorClass="text-primary bg-primary-soft" />
        <KpiCard title="Total Trips" value={overview.total_trips} icon={Map} colorClass="text-accent bg-accent-soft" />
        <KpiCard title="Total Stops" value={overview.total_stops} icon={Map} colorClass="text-info bg-info-soft" />
        <KpiCard title="New Trips (30d)" value={overview.trips_created_last_30_days} icon={TrendingUp} colorClass="text-success bg-success-soft" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Cities Chart / List */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-xl font-bold font-manrope text-text-primary mb-4">Popular Cities</h2>
            <div className="space-y-3">
              {cities.map((city, idx) => (
                <div key={city.city_id} className="flex justify-between items-center bg-surface-muted p-3 rounded-xl border border-border-subtle">
                  <div className="flex items-center gap-3">
                    <span className="font-bold text-text-muted w-4">{idx + 1}</span>
                    <div>
                      <p className="font-semibold text-text-primary">{city.name}</p>
                      <p className="text-xs text-text-secondary">{city.country}</p>
                    </div>
                  </div>
                  <Badge variant="primary">{city.stop_count} visits</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Top Activities Chart / List */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-xl font-bold font-manrope text-text-primary mb-4">Popular Activities</h2>
            <div className="space-y-3">
              {activities.map((act, idx) => (
                <div key={act.activity_id} className="flex justify-between items-center bg-surface-muted p-3 rounded-xl border border-border-subtle">
                  <div className="flex items-center gap-3">
                    <span className="font-bold text-text-muted w-4">{idx + 1}</span>
                    <div>
                      <p className="font-semibold text-text-primary truncate max-w-50 sm:max-w-62.5">{act.name}</p>
                      <p className="text-xs text-text-secondary">{act.city_name}</p>
                    </div>
                  </div>
                  <Badge variant="accent">{act.scheduled_count} schedules</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* User Management Table */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
            <h2 className="text-xl font-bold font-manrope text-text-primary">User Management</h2>
            <form onSubmit={handleSearchUsers} className="relative w-full sm:w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" size={16} />
              <input 
                type="text"
                placeholder="Search users..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="h-9 w-full rounded-xl border border-border-strong bg-input-background pl-9 pr-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-border-focus"
              />
            </form>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-surface-muted text-text-secondary border-b border-border-strong">
                <tr>
                  <th className="px-4 py-3 font-semibold">User</th>
                  <th className="px-4 py-3 font-semibold">Email</th>
                  <th className="px-4 py-3 font-semibold text-center">Role</th>
                  <th className="px-4 py-3 font-semibold text-right">Trips Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border-subtle bg-surface">
                {usersData.items.map(u => (
                  <tr key={u.id} className="hover:bg-surface-hover transition-colors">
                    <td className="px-4 py-3 font-medium text-text-primary">{u.first_name} {u.last_name}</td>
                    <td className="px-4 py-3 text-text-secondary">{u.email}</td>
                    <td className="px-4 py-3 text-center">
                      <Badge variant={u.is_admin ? "warning" : "default"}>{u.is_admin ? "Admin" : "User"}</Badge>
                    </td>
                    <td className="px-4 py-3 text-right font-bold text-text-primary">{u.trip_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

    </div>
  );
};

const KpiCard = ({ title, value, icon: Icon, colorClass }) => (
  <Card className="border-border-default shadow-sm">
    <CardContent className="p-5 flex items-center gap-4">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${colorClass}`}>
        <Icon size={24} />
      </div>
      <div>
        <p className="text-xs font-semibold text-text-secondary uppercase tracking-wider">{title}</p>
        <p className="text-2xl font-bold text-text-primary mt-0.5">{value?.toLocaleString()}</p>
      </div>
    </CardContent>
  </Card>
);