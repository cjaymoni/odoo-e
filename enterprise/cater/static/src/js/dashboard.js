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
          data = await this.env.services.rpc("/cater/dashboard_data");
          console.log("Data loaded successfully via rpc:", data);
        } catch (err) {
          console.warn("RPC method failed:", err);
        }
      }

      // Method 2: Try using env.services.orm
      if (!data && this.env.services && this.env.services.orm) {
        try {
          console.log("Attempting to load data via env.services.orm...");
          const result = await this.env.services.orm.call(
            "cater.dashboard",
            "get_dashboard_data",
            []
          );
          data = result;
          console.log("Data loaded successfully via orm:", data);
        } catch (err) {
          console.warn("ORM method failed:", err);
        }
      }

      // If we got data, update state
      if (data) {
        this.state.data = data;
        this.state.loading = false;
      } else {
        throw new Error(
          "Unable to load dashboard data. Please check your connection."
        );
      }
    } catch (error) {
      console.error("Dashboard loading error:", error);
      this.state.error = error.message || "Failed to load dashboard data";
      this.state.loading = false;
    }
  }

  formatCurrency(value) {
    if (typeof value !== "number") return "GH₵ 0.00";
    return `GH₵ ${value.toLocaleString("en-GH", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  }

  formatGrowth(value) {
    if (typeof value !== "number") return "0%";
    const sign = value >= 0 ? "+" : "";
    return `${sign}${value.toFixed(1)}%`;
  }

  getStarRating(rating) {
    if (typeof rating !== "number") return "☆☆☆☆☆";
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    let stars = "★".repeat(fullStars);
    if (hasHalfStar && fullStars < 5) stars += "⯨";
    stars += "☆".repeat(5 - fullStars - (hasHalfStar ? 1 : 0));
    return stars;
  }

  formatDate(dateStr) {
    if (!dateStr) return "";
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }
}

CateringDashboard.template = xml`
          <div class="catering-dashboard">
            <div class="dashboard-header d-flex flex-column flex-md-row align-items-start align-items-md-center justify-content-between">
              <div>
                <h1>🍽️ Catering Performance</h1>
                <p class="mb-0">Stay on top of bookings, revenue, and client happiness in one view.</p>
              </div>
              <button class="refresh-btn" t-on-click="loadDashboardData">
                <i class="fa fa-sync-alt"></i>
                Refresh Data
              </button>
            </div>

            <t t-if="state.loading">
              <div class="text-center py-5">
                <div class="spinner-border" role="status">
                  <span class="sr-only">Loading...</span>
                </div>
                <p class="mt-3 text-muted">Fetching the latest catering insights...</p>
              </div>
            </t>
            <t t-elif="state.error">
              <div class="alert alert-danger d-flex align-items-center" role="alert">
                <i class="fa fa-exclamation-triangle me-2"></i>
                <span><t t-esc="state.error"/></span>
              </div>
            </t>
            <t t-else="">
              <div class="container-fluid px-0">
                <div class="row">
                  <div class="col-lg-3 col-md-6 mb-4">
                    <div class="card kpi-card primary">
                      <div class="card-body p-4">
                        <div class="d-flex align-items-center justify-content-between">
                          <div>
                            <div class="kpi-label">Total Bookings (This Month)</div>
                            <div class="kpi-value"><t t-esc="state.data.kpis.total_bookings"/></div>
                            <div class="mt-2">
                              <span class="growth-indicator" t-att-class="'growth-indicator ' + (state.data.kpis.booking_growth >= 0 ? 'growth-positive' : 'growth-negative')">
                                <t t-esc="formatGrowth(state.data.kpis.booking_growth)"/>
                              </span>
                            </div>
                          </div>
                          <div class="kpi-icon primary">
                            <i class="fas fa-calendar-check"></i>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="col-lg-3 col-md-6 mb-4">
                    <div class="card kpi-card success">
                      <div class="card-body p-4">
                        <div class="d-flex align-items-center justify-content-between">
                          <div>
                            <div class="kpi-label">Monthly Revenue</div>
                            <div class="kpi-value"><t t-esc="formatCurrency(state.data.kpis.total_revenue)"/></div>
                            <div class="mt-2">
                              <span class="growth-indicator" t-att-class="'growth-indicator ' + (state.data.kpis.revenue_growth >= 0 ? 'growth-positive' : 'growth-negative')">
                                <t t-esc="formatGrowth(state.data.kpis.revenue_growth)"/>
                              </span>
                            </div>
                          </div>
                          <div class="kpi-icon success">
                            <i class="fas fa-money-bill-wave"></i>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="col-lg-3 col-md-6 mb-4">
                    <div class="card kpi-card info">
                      <div class="card-body p-4">
                        <div class="d-flex align-items-center justify-content-between">
                          <div>
                            <div class="kpi-label">Customer Satisfaction</div>
                            <div class="kpi-value"><t t-esc="state.data.kpis.avg_satisfaction"/>/5</div>
                            <div class="mt-2 text-warning" style="font-size: 1.2rem;">
                              <t t-esc="getStarRating(state.data.kpis.avg_satisfaction)"/>
                            </div>
                          </div>
                          <div class="kpi-icon info">
                            <i class="fas fa-star"></i>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="col-lg-3 col-md-6 mb-4">
                    <div class="card kpi-card warning">
                      <div class="card-body p-4">
                        <div class="d-flex align-items-center justify-content-between">
                          <div>
                            <div class="kpi-label">Active Customers</div>
                            <div class="kpi-value"><t t-esc="state.data.kpis.active_customers"/></div>
                            <div class="mt-2 text-muted" style="font-size: 0.9rem;">This month</div>
                          </div>
                          <div class="kpi-icon warning">
                            <i class="fas fa-users"></i>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="row mb-4">
                  <div class="col-lg-6 mb-4">
                    <div class="card content-card h-100">
                      <div class="card-header-gradient d-flex align-items-center justify-content-between">
                        <h6 class="mb-0"><i class="fa fa-comments me-2"></i>Customer Feedback Overview</h6>
                        <span class="badge badge-light" style="background: rgba(255,255,255,0.2); color: #fff;">
                          <t t-esc="state.data.feedback_summary.total_feedback"/> feedbacks
                        </span>
                      </div>
                      <div class="card-body p-4">
                        <div class="row align-items-center">
                          <div class="col-md-5 text-center">
                            <div class="rating-circle">
                              <div class="rating-value"><t t-esc="state.data.feedback_summary.avg_rating"/></div>
                              <div class="rating-stars">
                                <t t-esc="getStarRating(state.data.feedback_summary.avg_rating)"/>
                              </div>
                            </div>
                            <p class="text-muted mb-0" style="font-size: 0.9rem;">Average Rating</p>
                          </div>
                          <div class="col-md-7">
                            <div class="mb-3">
                              <div class="d-flex justify-content-between">
                                <span class="text-muted">Would Recommend</span>
                                <strong><t t-esc="state.data.feedback_summary.recommendation_rate"/>%</strong>
                              </div>
                              <div class="progress-modern">
                                <div class="progress-bar" style="background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);" t-att-style="'width: ' + state.data.feedback_summary.recommendation_rate + '%'">
                                </div>
                              </div>
                            </div>
                            <div class="mb-3">
                              <div class="d-flex justify-content-between">
                                <span class="text-muted">Response Rate</span>
                                <strong><t t-esc="state.data.feedback_summary.response_rate"/>%</strong>
                              </div>
                              <div class="progress-modern">
                                <div class="progress-bar" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);" t-att-style="'width: ' + state.data.feedback_summary.response_rate + '%'">
                                </div>
                              </div>
                            </div>
                            <div class="mb-2">
                              <div class="d-flex justify-content-between mb-1">
                                <small style="font-weight: 600; color: #2c3e50;">Food Quality</small>
                                <small style="font-weight: 700; color: #16a085;"><t t-esc="state.data.feedback_summary.detailed_ratings.food_quality"/>/5</small>
                              </div>
                              <div class="progress-modern">
                                <div class="progress-bar" style="background: linear-gradient(135deg, #43cea2 0%, #185a9d 100%);" t-att-style="'width: ' + (state.data.feedback_summary.detailed_ratings.food_quality * 20) + '%'">
                                </div>
                              </div>
                            </div>
                            <div class="mb-2">
                              <div class="d-flex justify-content-between mb-1">
                                <small style="font-weight: 600; color: #2c3e50;">Service</small>
                                <small style="font-weight: 700; color: #e67e22;"><t t-esc="state.data.feedback_summary.detailed_ratings.service_quality"/>/5</small>
                              </div>
                              <div class="progress-modern">
                                <div class="progress-bar" style="background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);" t-att-style="'width: ' + (state.data.feedback_summary.detailed_ratings.service_quality * 20) + '%'">
                                </div>
                              </div>
                            </div>
                            <div class="mb-2">
                              <div class="d-flex justify-content-between mb-1">
                                <small style="font-weight: 600; color: #2c3e50;">Presentation</small>
                                <small style="font-weight: 700; color: #c0392b;"><t t-esc="state.data.feedback_summary.detailed_ratings.presentation"/>/5</small>
                              </div>
                              <div class="progress-modern">
                                <div class="progress-bar" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);" t-att-style="'width: ' + (state.data.feedback_summary.detailed_ratings.presentation * 20) + '%'">
                                </div>
                              </div>
                            </div>
                            <div>
                              <div class="d-flex justify-content-between mb-1">
                                <small style="font-weight: 600; color: #2c3e50;">Timeliness</small>
                                <small style="font-weight: 700; color: #9b59b6;"><t t-esc="state.data.feedback_summary.detailed_ratings.timeliness"/>/5</small>
                              </div>
                              <div class="progress-modern">
                                <div class="progress-bar" style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);" t-att-style="'width: ' + (state.data.feedback_summary.detailed_ratings.timeliness * 20) + '%'">
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="col-lg-6 mb-4">
                    <div class="card content-card h-100">
                      <div class="card-header-gradient">
                        <h6 class="mb-0"><i class="fa fa-history me-2"></i>Recent Activity</h6>
                      </div>
                      <div class="card-body p-4" style="max-height: 420px; overflow-y: auto;">
                        <div t-if="state.data.recent_activity and state.data.recent_activity.length">
                          <div t-foreach="state.data.recent_activity" t-as="activity" t-key="activity_index" class="activity-item">
                            <div class="d-flex align-items-start">
                              <div class="activity-icon">
                                <i t-att-class="'fa fa-' + (activity.icon || 'bell')"></i>
                              </div>
                              <div class="flex-grow-1">
                                <h6 class="mb-1" style="font-weight: 600; color: #2c3e50;">
                                  <t t-esc="activity.title"/>
                                </h6>
                                <p class="mb-1" style="font-size: 0.9rem; color: #7f8c8d;">
                                  <t t-esc="activity.description"/>
                                </p>
                                <small style="color: #95a5a6;">
                                  <i class="fa fa-clock"></i>
                                  <t t-esc="activity.date ? formatDate(activity.date) : ''"/>
                                </small>
                              </div>
                            </div>
                          </div>
                        </div>
                        <div t-else="" class="text-center py-5">
                          <i class="fa fa-inbox fa-3x" style="color: #bdc3c7;"></i>
                          <p class="mt-3 text-muted mb-0">No recent activity</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="row mb-4">
                  <div class="col-12">
                    <div class="card content-card">
                      <div class="card-header-gradient d-flex align-items-center justify-content-between">
                        <h6 class="mb-0"><i class="fa fa-calendar-check me-2"></i>Upcoming Events (Next 7 Days)</h6>
                        <span class="badge badge-light" style="background: rgba(255,255,255,0.2); color: #fff;">
                          <t t-esc="state.data.upcoming_events ? state.data.upcoming_events.length : 0"/> events
                        </span>
                      </div>
                      <div class="card-body p-0">
                        <div class="table-responsive">
                          <table class="table table-modern mb-0">
                            <thead>
                              <tr>
                                <th><i class="fa fa-tag"></i> Event</th>
                                <th><i class="fa fa-user"></i> Customer</th>
                                <th><i class="fa fa-calendar"></i> Date</th>
                                <th><i class="fa fa-map-marker-alt"></i> Venue</th>
                                <th><i class="fa fa-users"></i> Guests</th>
                                <th><i class="fa fa-info-circle"></i> Status</th>
                                <th><i class="fa fa-money-bill"></i> Total</th>
                              </tr>
                            </thead>
                            <tbody>
                              <tr t-foreach="state.data.upcoming_events" t-as="event" t-key="event.id">
                                <td style="font-weight: 600; color: #667eea;">
                                  <t t-esc="event.name"/>
                                </td>
                                <td>
                                  <i class="fa fa-user-circle" style="color: #95a5a6;"></i>
                                  <t t-esc="event.customer"/>
                                </td>
                                <td>
                                  <t t-esc="formatDate(event.date)"/>
                                </td>
                                <td>
                                  <t t-esc="event.venue"/>
                                </td>
                                <td>
                                  <strong><t t-esc="event.guests"/></strong>
                                </td>
                                <td>
                                  <span t-if="event.status === 'confirmed'" class="badge badge-modern badge-success-modern">
                                    <i class="fa fa-check-circle"></i> Confirmed
                                  </span>
                                  <span t-elif="event.status === 'draft'" class="badge badge-modern badge-warning-modern">
                                    <i class="fa fa-clock"></i> Draft
                                  </span>
                                  <span t-elif="event.status === 'in_progress'" class="badge badge-modern badge-info-modern">
                                    <i class="fa fa-tasks"></i> In Progress
                                  </span>
                                  <span t-else="" class="badge badge-modern badge-info-modern">
                                    <t t-esc="event.status"/>
                                  </span>
                                </td>
                                <td style="font-weight: 700; color: #27ae60;">
                                  <t t-esc="formatCurrency(event.total || 0)"/>
                                </td>
                              </tr>
                              <tr t-if="!state.data.upcoming_events || !state.data.upcoming_events.length">
                                <td colspan="7" class="text-center py-5">
                                  <i class="fa fa-calendar-times fa-3x" style="color: #bdc3c7;"></i>
                                  <p class="mt-3 text-muted mb-0">No upcoming events scheduled</p>
                                </td>
                              </tr>
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </t>
          </div>
          `;

registry.category("actions").add("catering_dashboard", CateringDashboard);
