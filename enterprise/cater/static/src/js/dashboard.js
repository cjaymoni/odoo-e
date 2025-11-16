/** @odoo-module **/

import { Component, onWillStart, useState, xml } from "@odoo/owl";
import { registry } from "@web/core/registry";

class CateringDashboard extends Component {
  setup() {
    this.state = useState({
      data: null,
      loading: true,
      error: null,
    });

    onWillStart(async () => {
      await this.loadDashboardData();
    });
  }

  async loadDashboardData() {
    try {
      this.state.loading = true;
      this.state.error = null;

      // Try to access data using the environment services
      let data = null;

      // Method 1: Try using env.services.rpc
      if (this.env.services && this.env.services.rpc) {
        try {
          console.log("Attempting to load data via env.services.rpc...");
          data = await this.env.services.rpc("/web/dataset/call_kw", {
            model: "cater.dashboard",
            method: "get_dashboard_data",
            args: [],
            kwargs: {},
          });
          console.log("Successfully loaded data via env.services.rpc:", data);
        } catch (rpcError) {
          console.error("env.services.rpc failed:", rpcError);
        }
      }

      // Method 2: Try direct fetch if env.services.rpc failed
      if (!data) {
        try {
          console.log("Attempting to load data via direct fetch...");
          const response = await fetch("/web/dataset/call_kw", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            credentials: "include",
            body: JSON.stringify({
              jsonrpc: "2.0",
              method: "call",
              params: {
                model: "cater.dashboard",
                method: "get_dashboard_data",
                args: [],
                kwargs: {},
              },
              id: Math.floor(Math.random() * 1000000),
            }),
          });

          if (response.ok) {
            const result = await response.json();
            if (result.result) {
              data = result.result;
              console.log("Successfully loaded data via fetch:", data);
            } else if (result.error) {
              console.error("Backend error:", result.error);
            }
          }
        } catch (fetchError) {
          console.error("Fetch method failed:", fetchError);
        }
      }

      // Check if we have valid data
      if (data && typeof data === "object" && data.kpis) {
        this.state.data = data;
        console.log("Successfully loaded real data with values:", {
          total_bookings: data.kpis.total_bookings,
          total_revenue: data.kpis.total_revenue,
          avg_satisfaction: data.kpis.avg_satisfaction,
          active_customers: data.kpis.active_customers,
        });
        return;
      }

      // Fallback to mock data if all methods failed
      console.warn("All data loading methods failed, using mock data");
      this.state.error = "Using demo data - unable to connect to backend";
      this.state.data = this.getMockData();
    } catch (error) {
      console.error("Error loading dashboard data:", error);
      this.state.error = "Failed to load dashboard data. Using demo data.";
      this.state.data = this.getMockData();
    } finally {
      this.state.loading = false;
    }
  }

  getMockData() {
    return {
      kpis: {
        total_bookings: 25,
        booking_growth: 15.5,
        total_revenue: 12500.0,
        revenue_growth: 8.2,
        avg_satisfaction: 4.3,
        active_customers: 18,
      },
      feedback_summary: {
        avg_rating: 4.3,
        response_rate: 75,
      },
      recent_activity: [
        {
          title: "New Booking Created",
          description: "Wedding event scheduled for next month",
        },
        {
          title: "Feedback Received",
          description: "5-star rating for birthday party catering",
        },
        {
          title: "Payment Received",
          description: "GHS 2,500 payment confirmed",
        },
      ],
      upcoming_events: [
        {
          id: 1,
          name: "Corporate Lunch",
          customer: "ABC Corp",
          date: "2025-09-20",
          guests: 50,
          status: "Confirmed",
        },
        {
          id: 2,
          name: "Wedding Reception",
          customer: "John & Mary",
          date: "2025-09-25",
          guests: 150,
          status: "In Progress",
        },
      ],
    };
  }

  formatCurrency(amount) {
    return new Intl.NumberFormat("en-GH", {
      style: "currency",
      currency: "GHS",
    }).format(amount);
  }

  formatGrowth(growth) {
    const icon = growth >= 0 ? "↗" : "↘";
    const color = growth >= 0 ? "text-success" : "text-danger";
    return `${icon} ${Math.abs(growth)}%`;
  }

  formatDate(dateString) {
    return new Date(dateString).toLocaleDateString("en-GH", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  getStarRating(rating) {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      if (i <= rating) {
        stars.push("★");
      } else {
        stars.push("☆");
      }
    }
    return stars.join("");
  }
}

CateringDashboard.template = xml`
<div class="catering-dashboard">
  <div class="d-sm-flex align-items-center justify-content-between mb-4">
    <h1 class="h3 mb-0 text-gray-800">Catering Dashboard</h1>
    <button class="btn btn-primary btn-sm" t-on-click="loadDashboardData">
      <i class="fa fa-sync-alt fa-sm text-white-50"></i> Refresh
    </button>
  </div>

  <div t-if="state.loading" class="text-center">
    <div class="spinner-border" role="status">
      <span class="sr-only">Loading...</span>
    </div>
    <p class="mt-2">Loading dashboard data...</p>
  </div>

        <div t-if="state.error" class="alert alert-warning mb-3" role="alert">
          <i class="fa fa-exclamation-triangle me-2"></i>
          <t t-esc="state.error"/>
        </div>  <div t-if="state.data and !state.loading">
    <!-- KPI Cards -->
    <div class="row">
      <div class="col-lg-3 col-md-6 mb-4">
        <div class="card border-left-primary shadow h-100 py-2">
          <div class="card-body">
            <div class="row no-gutters align-items-center">
              <div class="col mr-2">
                <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">
                  Total Bookings (This Month)
                </div>
                <div class="h5 mb-0 font-weight-bold text-gray-800">
                  <t t-esc="state.data.kpis ? state.data.kpis.total_bookings : 0"/>
                </div>
                <div class="mt-1">
                  <span t-att-class="'text-' + ((state.data.kpis and state.data.kpis.booking_growth >= 0) ? 'success' : 'danger')">
                    <t t-esc="state.data.kpis ? formatGrowth(state.data.kpis.booking_growth) : 'N/A'"/>
                  </span>
                </div>
              </div>
              <div class="col-auto">
                <i class="fa fa-calendar-alt fa-2x text-gray-300"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-3 col-md-6 mb-4">
        <div class="card border-left-success shadow h-100 py-2">
          <div class="card-body">
            <div class="row no-gutters align-items-center">
              <div class="col mr-2">
                <div class="text-xs font-weight-bold text-success text-uppercase mb-1">
                  Monthly Revenue
                </div>
                <div class="h5 mb-0 font-weight-bold text-gray-800">
                  <t t-esc="state.data.kpis ? formatCurrency(state.data.kpis.total_revenue) : 'GHS 0'"/>
                </div>
                <div class="mt-1">
                  <span t-att-class="'text-' + ((state.data.kpis and state.data.kpis.revenue_growth >= 0) ? 'success' : 'danger')">
                    <t t-esc="state.data.kpis ? formatGrowth(state.data.kpis.revenue_growth) : 'N/A'"/>
                  </span>
                </div>
              </div>
              <div class="col-auto">
                <i class="fa fa-dollar-sign fa-2x text-gray-300"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-3 col-md-6 mb-4">
        <div class="card border-left-info shadow h-100 py-2">
          <div class="card-body">
            <div class="row no-gutters align-items-center">
              <div class="col mr-2">
                <div class="text-xs font-weight-bold text-info text-uppercase mb-1">
                  Customer Satisfaction
                </div>
                <div class="h5 mb-0 font-weight-bold text-gray-800">
                  <t t-esc="state.data.kpis ? state.data.kpis.avg_satisfaction.toFixed(1) : '0.0'"/>/5.0
                </div>
              </div>
              <div class="col-auto">
                <i class="fa fa-star fa-2x text-gray-300"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-3 col-md-6 mb-4">
        <div class="card border-left-warning shadow h-100 py-2">
          <div class="card-body">
            <div class="row no-gutters align-items-center">
              <div class="col mr-2">
                <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">
                  Active Customers
                </div>
                <div class="h5 mb-0 font-weight-bold text-gray-800">
                  <t t-esc="state.data.kpis ? state.data.kpis.active_customers : 0"/>
                </div>
              </div>
              <div class="col-auto">
                <i class="fa fa-users fa-2x text-gray-300"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activity and Feedback -->
    <div class="row">
      <div class="col-lg-6">
        <div class="card shadow mb-4">
          <div class="card-header py-3">
            <h6 class="m-0 font-weight-bold text-primary">Customer Feedback Summary</h6>
          </div>
          <div class="card-body">
            <div class="text-center">
              <h3><t t-esc="state.data.feedback_summary ? state.data.feedback_summary.avg_rating : 0"/>/5</h3>
              <p class="text-muted">Average Rating</p>
              <p><strong>Response Rate:</strong> <t t-esc="state.data.feedback_summary ? state.data.feedback_summary.response_rate : 0"/>%</p>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-6">
        <div class="card shadow mb-4">
          <div class="card-header py-3">
            <h6 class="m-0 font-weight-bold text-primary">Recent Activity</h6>
          </div>
          <div class="card-body">
            <div t-if="state.data.recent_activity">
              <div t-foreach="state.data.recent_activity" t-as="activity" t-key="activity_index">
                <p><strong><t t-esc="activity.title"/></strong><br/>
                <small class="text-muted"><t t-esc="activity.description"/></small></p>
              </div>
            </div>
            <div t-else="">
              <p class="text-muted">No recent activity</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Upcoming Events -->
    <div class="row">
      <div class="col-12">
        <div class="card shadow mb-4">
          <div class="card-header py-3">
            <h6 class="m-0 font-weight-bold text-primary">Upcoming Events</h6>
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-bordered">
                <thead>
                  <tr>
                    <th>Event</th>
                    <th>Customer</th>
                    <th>Date</th>
                    <th>Guests</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr t-if="!state.data.upcoming_events or state.data.upcoming_events.length === 0">
                    <td colspan="5" class="text-center text-muted">No upcoming events</td>
                  </tr>
                  <tr t-foreach="state.data.upcoming_events || []" t-as="event" t-key="event.id">
                    <td><t t-esc="event.name"/></td>
                    <td><t t-esc="event.customer"/></td>
                    <td><t t-esc="formatDate(event.date)"/></td>
                    <td><t t-esc="event.guests"/></td>
                    <td><t t-esc="event.status"/></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
`;

registry.category("actions").add("catering_dashboard", CateringDashboard);
