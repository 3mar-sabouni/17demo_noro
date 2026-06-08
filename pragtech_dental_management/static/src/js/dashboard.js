/** @odoo-module */

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { loadJS } from "@web/core/assets";
import { jsonrpc } from "@web/core/network/rpc_service";
const { Component, onWillStart, useRef, onMounted, useState } = owl;

export class DentalDashboard extends Component {
  setup() {
    this.ChartServiceAppointment = useRef("chart");
    this.ChartDoctorAppointment = useRef("chart1");
    this.ChartDoctorRevenue = useRef("chart2");
    this.actionService = useService("action");
    this.orm = useService("orm");
    this.rpc = useService("rpc");
    onMounted(this.onMounted);

    onWillStart(async () => {
      await loadJS(
        "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"
      );
    });
  }
  onMounted() {
    this.getAppointments();
    this.getTodaysAppointments();
    this.getRevenue();
    this.getPendingComplaints();
    this.getPatient();
    this.getPrescriptions();
    this.ServiceBasedAppoinment();
    this.DoctorBasedAppoinment();
    this.doctors_per_revenue_chart();
  }

  async onChangePeriod() {
    const period = document.getElementById("onchangeperiod").value;
    const date = luxon.DateTime
      .now()
      .minus({ days: period })
      .toFormat("MM-dd-yyyy HH:mm:ss");
    await this. getAppointments(period);  
    await this.getRevenue(period);
    await this.getPatient(period);
    await this.getPrescriptions(period);
    await this.ServiceBasedAppoinment(period);
    await this.DoctorBasedAppoinment(period);
    await this.doctors_per_revenue_chart(period);
  }

  // Appointment Details
  async getAppointments(period) {
    try {
      const startDate = luxon.DateTime.now().minus({ days: period }).toISODate();
      let domain = [['appointment_sdate', '>=', startDate]]
      const data = await this.orm.searchCount("medical.appointment", domain)
      const datas = document.getElementById("appointment_count");
      datas.textContent = data;
    } catch (error) {
      console.error("Error fetching appointments records", error);
    }
  }

  async onClickAppointmentBtn() {
    try {
      var self = this;
      const period = document.getElementById("onchangeperiod").value;
      const startDate = luxon.DateTime
        .now()
        .minus({ days: period })
        .toISODate();
      self.actionService.doAction({
        name: _t("Appointments"),
        res_model: "medical.appointment",
        views: [[false, "tree"], [false, "form"]],
        view_mode: "tree,form",
        type: "ir.actions.act_window",
        target: "current",
        domain:[['appointment_sdate', '>=', startDate]],
        context: {}
      });
    } catch (error) {
      console.error("Error fetching appointment view records", error);
    }
  }

  // todaysaAppoinmentdetails
  async getTodaysAppointments() {
    try {
      const startOfToday = new Date();
      startOfToday.setHours(0, 0, 0, 0);
      const datas = document.getElementById("todays_appointment_count");
      const endOfToday = new Date();
      endOfToday.setHours(23, 59, 59, 999);
      const data = await this.orm.searchCount("medical.appointment", [
        ["appointment_sdate", ">=", startOfToday.toISOString()],
        ["appointment_edate", "<=", endOfToday.toISOString()]
      ]);
      datas.textContent = data;
    } catch (error) {
      console.error("Error fetching todays appointments:", error);
    }
  }

  async onClickTodaysAppointmentBtn() {
    try {
      const startOfToday = new Date();
      startOfToday.setHours(0, 0, 0, 0);

      const endOfToday = new Date();
      endOfToday.setHours(23, 59, 59, 999);
      var self = this;
      self.actionService.doAction({
        name: _t("Todays Appointment"),
        res_model: "medical.appointment",
        views: [[false, "tree"], [false, "form"]],
        view_mode: "tree,form",
        type: "ir.actions.act_window",
        target: "current",
        domain: [
          ["appointment_sdate", ">=", startOfToday.toISOString()],
          ["appointment_edate", "<=", endOfToday.toISOString()]
        ],
        context: {}
      });
    } catch (error) {
      console.error("Error fetching  todays appointments view:", error);
    }
  }

  // Pending Complaints
  async getPendingComplaints() {
    try {
      const datas = document.getElementById("pending_complaints");
      let domain = [["state", "=", "pending"]];
      const data = await this.orm.searchCount("patient.complaint", domain);
      datas.textContent = data;
    } catch (error) {
      console.error("Error fetching pending complaints", error);
    }
  }

  async onClickPendingComplaintBtn() {
    try {
      var self = this;
      self.actionService.doAction({
        name: _t("Pending Compaint"),
        res_model: "patient.complaint",
        views: [[false, "tree"], [false, "form"]],
        view_mode: "tree,form",
        type: "ir.actions.act_window",
        target: "current",
        domain: [["state", "=", "pending"]],
        context: {}
      });
    } catch (error) {
      console.error("Error fetching revenue view list", error);
    }
  }

  //  Patient Details
  async getPatient(period) {
    try {
      var startDate = luxon.DateTime.now().minus({ days: period }).toISODate();
      let domain = [["date", ">=", startDate]];
      const data = await this.orm.searchCount("medical.patient", domain);
      const datas = document.getElementById("patient_details");
      datas.textContent = data;
    } catch (error) {
      console.error("Error fetching Patient details", error);
    }
  }

  async onClickPatientBtn() {
    try {
      var self = this;
      const period = document.getElementById("onchangeperiod").value;
      const startDate = luxon.DateTime
        .now()
        .minus({ days: period })
        .toISODate();
      self.actionService.doAction({
        name: _t("Patients"),
        res_model: "medical.patient",
        views: [[false, "tree"], [false, "form"]],
        view_mode: "tree,form",
        type: "ir.actions.act_window",
        target: "current",
        domain: [["date", ">=", startDate]],
        context: {}
      });
    } catch (error) {
      console.error("Error fetching revenue view list", error);
    }
  }


    // prescriptions
    async getPrescriptions(period) {
      try {
      var startDate = luxon.DateTime.now().minus({ days: period }).toISODate();
      let domain = [["prescription_date", ">=", startDate]];
      const data = await this.orm.searchCount("medical.prescription.order", domain);
      const datas = document.getElementById("prescription_count");
      datas.textContent = data;
      } catch (error) {
      console.error("Error fetching Prescription details", error);
      }
  }

    async onClickPrescriptionCountBtn() {
      try {
      var self = this;
      const period = document.getElementById("onchangeperiod").value;
      const startDate = luxon.DateTime
          .now()
          .minus({ days: period })
          .toISODate();
      self.actionService.doAction({
          name: _t("Prescriptions"),
          res_model: "medical.prescription.order",
          views: [[false, "tree"], [false, "form"]],
          view_mode: "tree,form",
          type: "ir.actions.act_window",
          target: "current",
          domain: [["prescription_date", ">=", startDate]],
          context: {}
      });
      } catch (error) {
      console.error("Error fetching prescription view list", error);
      }
  }

  // revenue details
  async getRevenue(period) {
    try {
      var startDate = luxon.DateTime.now().minus({ days: period }).toISODate();
      var data = await this.orm.call(
        "account.move",
        "fetching_all_invoice_total",
        [0],
        { startDate }
      );
      const datas = document.getElementById("revenue");
      datas.textContent = "$" + data;
    } catch (error) {
      console.error("Error fetching revenue", error);
    }
  }

  async onClickrevenuetBtn() {
    try {
      var self = this;
      const period = document.getElementById("onchangeperiod").value;
      const startDate = luxon.DateTime
        .now()
        .minus({ days: period })
        .toISODate();
      self.actionService.doAction({
        name: _t("Revenue"),
        res_model: "account.move",
        views: [[false, "tree"], [false, "form"]],
        view_mode: "tree,form",
        type: "ir.actions.act_window",
        target: "current",
        domain: [
          ["invoice_date", ">=", startDate],
          ["payment_state", "=", "paid"]
        ],
        context: {}
      });
    } catch (error) {
      console.error("Error fetching revenue view list", error);
    }
  }

  // <------------------------------------------------------Chart View----------------------------------------->

  // Service Based Appointment chart
  async ServiceBasedAppoinment(period) {
    try {
      const startDate = luxon.DateTime
      .now()
      .minus({ days: period })
      .toISODate();
      let domain = [['appointment_sdate', '>=', startDate]]
      const datas = await this.orm.readGroup(
        "medical.appointment",
        domain,
        ["service_id"],
        ["service_id"]
      );
      const chartCanvas = document.getElementById("appointment_chart");
      // Check if a chart instance already exists
      if (chartCanvas.chart) {
        chartCanvas.chart.destroy(); // Destroy the existing chart instance
      }
      chartCanvas.chart = new Chart(chartCanvas, {
        type: "bar",
        data: {
          labels: datas.map(d => d.service_id[1]),
          datasets: [
            {
              label: "Appoinment Count",
              data: datas.map(d => d.service_id_count),
              backgroundColor: "rgba(255, 99, 132, 0.2)",
              borderColor: "rgba(255, 99, 132, 1)",
              borderWidth: 1
            }
          ]
        }
      });
    } catch (error) {
      console.error("Error fetching service based appointment chart", error);
    }
  }

  // Doctor based Appointment Chart

  async DoctorBasedAppoinment(period) {
    try {
      const startDate = luxon.DateTime
      .now()
      .minus({ days: period })
      .toISODate();

      let domain = [['appointment_sdate', '>=', startDate]]
      const datas = await this.orm.readGroup(
        "medical.appointment",
        domain,
        ["doctor"],
        ["doctor"]
      );
      const chartCanvas = document.getElementById("doctor_appointment_chart")
      if (chartCanvas.chart1) {
        chartCanvas.chart1.destroy(); // Destroy the existing chart instance
      }
      chartCanvas.chart1 = new Chart(chartCanvas, {
        type: "bar",
        data: {
          labels: datas.map(d => d.doctor[1]),
          datasets: [
            {
              label: "Appoinment Count",
              data: datas.map(d => d.doctor_count),
              backgroundColor: "rgba(255, 165, 0, 0.5)",
              borderColor: "rgba(255, 99, 132, 1)",
              borderWidth: 1
            }
          ]
        }
      });
    } catch (error) {
      console.error("Error fetching doctot based appointmnt chart", error);
    }
  }

  // doctor based revenue chart
  async doctors_per_revenue_chart(period) {
    try {
      var startDate = luxon.DateTime.now().minus({ days: period }).toISODate();
      var data = await this.orm.call(
        "account.move",
        "fetching_all_doctors_revenue",
        [0],
        { startDate },
      );
      const chartCanvas = document.getElementById("doctor_revenue")
      if (chartCanvas.chart2) {
        chartCanvas.chart2.destroy(); // Destroy the existing chart instance
      }
      data.forEach(record => {});
      const labels = data.map(record => record.doctor_name);
      const revenues = data.map(record => record.revenue);

      chartCanvas.chart2 = new Chart(chartCanvas,{
        type: "bar",
        data: {
          labels: labels,
          datasets: [
            {
              label: "Revenue",
              data: revenues,
              backgroundColor: "rgba(75, 192, 192, 0.2)", // Light teal with transparency
              borderColor: "rgba(75, 192, 192, 1)",
              borderWidth: 1
            }
          ]
        }
      });
    } catch (error) {
      console.error("Error fetching doctor based revenue chart", error);
    }
  }
}

DentalDashboard.template = "dental_management.dashboard";
// OdooDashboard.components = { KpiCard }

registry.category("actions").add("dental_dashboard.dashboard", DentalDashboard);
