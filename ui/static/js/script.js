// Generic AI Audit Agent - JavaScript

document.addEventListener("DOMContentLoaded", function () {
  // Tab Navigation
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabPanes = document.querySelectorAll(".tab-pane");

  tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      // Remove active class from all buttons and panes
      tabButtons.forEach((btn) => btn.classList.remove("active"));
      tabPanes.forEach((pane) => pane.classList.remove("active"));

      // Add active class to clicked button and corresponding pane
      button.classList.add("active");
      const tabId = button.getAttribute("data-tab");
      document.getElementById(tabId).classList.add("active");
    });
  });

  // Custom Fields Management
  const customFieldsContainer = document.getElementById(
    "custom-fields-container"
  );
  const addCustomFieldButton = document.getElementById("add-custom-field");
  const customFieldTemplate = document.getElementById("custom-field-template");
  let customFieldCounter = 0;

  addCustomFieldButton.addEventListener("click", () => {
    addCustomField();
  });

  function addCustomField() {
    customFieldCounter++;
    const fieldId = customFieldCounter;

    // Clone the template content
    const templateContent = customFieldTemplate.innerHTML;

    // Replace placeholder IDs with actual IDs
    const fieldHtml = templateContent.replace(/{id}/g, fieldId);

    // Create a container for the new field
    const fieldContainer = document.createElement("div");
    fieldContainer.innerHTML = fieldHtml;

    // Add the field to the container
    customFieldsContainer.appendChild(fieldContainer.firstElementChild);

    // Add event listener to the remove button
    const removeButton = customFieldsContainer
      .querySelector(`#custom-field-name-${fieldId}`)
      .closest(".custom-field")
      .querySelector(".remove-custom-field");
    removeButton.addEventListener("click", function () {
      this.closest(".custom-field").remove();
    });

    // Show advanced selector if advanced options are visible
    if (!advancedSelectors.classList.contains("hidden")) {
      const advancedSelector = customFieldsContainer
        .querySelector(`#custom-field-name-${fieldId}`)
        .closest(".custom-field")
        .querySelector(".advanced-selector");
      advancedSelector.classList.remove("hidden");
    }
  }

  // Toggle Advanced Options
  const toggleAdvancedButton = document.getElementById("toggle-advanced");
  const advancedSelectors = document.getElementById("advanced-selectors");

  toggleAdvancedButton.addEventListener("click", () => {
    advancedSelectors.classList.toggle("hidden");
    toggleAdvancedButton.innerHTML = advancedSelectors.classList.contains(
      "hidden"
    )
      ? '<i class="fas fa-cog"></i> Advanced Options'
      : '<i class="fas fa-cog"></i> Hide Advanced Options';
  });

  // Start Audit Button
  const startAuditButton = document.getElementById("start-audit");
  startAuditButton.addEventListener("click", startAudit);

  function startAudit() {
    // Validate form
    const startUrl = document.getElementById("start-url").value;
    const allowedDomain = document.getElementById("allowed-domain").value;

    if (!startUrl || !allowedDomain) {
      alert("Starting URL and Allowed Domain are required!");
      return;
    }

    // Collect configuration
    const config = {
      start_url: startUrl,
      allowed_domain: allowedDomain,
      report_formats: getSelectedReportFormats(),
      product_url_patterns: getTextareaValues("product-url-patterns"),
      product_page_selectors: getTextareaValues("product-page-selectors"),
      extract_fields: getSelectedDataFields(),
      custom_fields: getCustomFields(),
    };

    // Add crawl limit if not set to "no limit"
    const noLimit = document.getElementById("no-limit").checked;
    if (!noLimit) {
      const crawlLimit = document.getElementById("crawl-limit").value;
      config.crawl_limit = parseInt(crawlLimit);
    }

    // Add selectors if advanced options are used
    if (!advancedSelectors.classList.contains("hidden")) {
      config.product_name_selectors = getTextareaValues(
        "product-name-selectors"
      );
      config.product_price_selectors = getTextareaValues(
        "product-price-selectors"
      );
      config.product_description_selectors = getTextareaValues(
        "product-description-selectors"
      );
      config.product_sku_selectors = getTextareaValues("product-sku-selectors");
      config.product_image_selectors = getTextareaValues(
        "product-image-selectors"
      );
      config.product_specs_selectors = getTextareaValues(
        "product-specs-selectors"
      );
    }

    // Switch to status tab
    document.querySelector('.tab-btn[data-tab="status"]').click();

    // Start the audit
    fetch("/start_audit", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(config),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          // Start polling for status updates
          startStatusPolling();
        } else {
          alert(`Error: ${data.message}`);
        }
      })
      .catch((error) => {
        console.error("Error starting audit:", error);
        alert("Failed to start audit. See console for details.");
      });
  }

  function getTextareaValues(id) {
    const textarea = document.getElementById(id);
    if (!textarea || !textarea.value.trim()) {
      return [];
    }

    return textarea.value
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line.length > 0);
  }

  function getSelectedReportFormats() {
    const formats = [];
    if (document.getElementById("report-text").checked) formats.push("text");
    if (document.getElementById("report-html").checked) formats.push("html");
    if (document.getElementById("report-csv").checked) formats.push("csv");
    return formats;
  }

  function getSelectedDataFields() {
    const fields = [];
    if (document.getElementById("extract-name").checked) fields.push("name");
    if (document.getElementById("extract-price").checked) fields.push("price");
    if (document.getElementById("extract-description").checked)
      fields.push("description");
    if (document.getElementById("extract-sku").checked) fields.push("sku");
    if (document.getElementById("extract-images").checked)
      fields.push("images");
    if (document.getElementById("extract-specs").checked) fields.push("specs");
    return fields;
  }

  function getCustomFields() {
    const customFields = {};
    const fieldElements = document.querySelectorAll(".custom-field");

    fieldElements.forEach((element) => {
      const nameInput = element.querySelector(".custom-field-name");
      const selectorInput = element.querySelector(".custom-field-selector");

      if (nameInput && nameInput.value.trim()) {
        // If selector is provided, use it; otherwise, use a default selector based on field name
        if (selectorInput && selectorInput.value.trim()) {
          customFields[nameInput.value.trim()] = selectorInput.value.trim();
        } else {
          // Create a default selector based on common patterns
          const fieldName = nameInput.value.trim().toLowerCase();
          customFields[
            fieldName
          ] = `.${fieldName}::text, [itemprop="${fieldName}"]::text, .product-${fieldName}::text`;
        }
      }
    });

    return customFields;
  }

  // Status Polling
  let statusPollingInterval;

  function startStatusPolling() {
    // Clear any existing polling
    if (statusPollingInterval) {
      clearInterval(statusPollingInterval);
    }

    // Poll every 2 seconds
    statusPollingInterval = setInterval(updateStatus, 2000);

    // Initial update
    updateStatus();
  }

  function stopStatusPolling() {
    if (statusPollingInterval) {
      clearInterval(statusPollingInterval);
      statusPollingInterval = null;
    }
  }

  function updateStatus() {
    fetch("/audit_status")
      .then((response) => response.json())
      .then((data) => {
        updateStatusDisplay(data);

        // If audit is no longer running, stop polling and update reports
        if (!data.running && data.step === "completed") {
          stopStatusPolling();
          updateReports();
        }
      })
      .catch((error) => {
        console.error("Error fetching status:", error);
      });
  }

  function updateStatusDisplay(data) {
    // Update status value
    const statusValue = document.getElementById("status-value");
    statusValue.textContent = data.running
      ? "Running"
      : data.step === "completed"
      ? "Completed"
      : "Not running";
    statusValue.className = "status-value";
    if (data.running) {
      statusValue.classList.add("status-running");
    } else if (data.step === "completed") {
      statusValue.classList.add("status-completed");
    }

    // Update step value
    const stepValue = document.getElementById("step-value");
    stepValue.textContent = data.step ? capitalizeFirstLetter(data.step) : "-";

    // Update progress bar
    const progressBar = document.getElementById("progress-bar");
    const progressValue = document.getElementById("progress-value");
    progressBar.style.width = `${data.progress}%`;
    progressValue.textContent = `${data.progress}%`;

    // Update log
    const logContainer = document.getElementById("log-container");
    logContainer.innerHTML = "";

    data.log.forEach((message) => {
      const logLine = document.createElement("div");
      logLine.className = "log-line";
      logLine.textContent = message;
      logContainer.appendChild(logLine);
    });

    // Scroll to bottom of log
    logContainer.scrollTop = logContainer.scrollHeight;
  }

  function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
  }

  // Clear Log Button
  const clearLogButton = document.getElementById("clear-log");
  clearLogButton.addEventListener("click", clearLog);

  // Stop Audit Button
  const stopAuditButton = document.getElementById("stop-audit");
  stopAuditButton.addEventListener("click", stopAudit);

  function stopAudit() {
    if (
      confirm(
        "Are you sure you want to stop the audit? This will generate reports with the data collected so far."
      )
    ) {
      fetch("/stop_audit", {
        method: "POST",
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.status === "success") {
            alert("Audit stopped. Generating reports with collected data.");
            updateReports();
          } else {
            alert(`Error: ${data.message}`);
          }
        })
        .catch((error) => {
          console.error("Error stopping audit:", error);
          alert("Failed to stop audit. See console for details.");
        });
    }
  }

  function clearLog() {
    fetch("/clear_log")
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          document.getElementById("log-container").innerHTML = "";
        }
      })
      .catch((error) => {
        console.error("Error clearing log:", error);
      });
  }

  // Reports Tab
  function updateReports() {
    fetch("/reports")
      .then((response) => response.json())
      .then((data) => {
        displayReports(data);
      })
      .catch((error) => {
        console.error("Error fetching reports:", error);
      });
  }

  function displayReports(reports) {
    // Update text reports
    const textReportsList = document.getElementById("text-reports");
    textReportsList.innerHTML = "";

    if (reports.text.length === 0) {
      textReportsList.innerHTML =
        '<li class="no-reports">No text reports available</li>';
    } else {
      reports.text
        .sort()
        .reverse()
        .forEach((report) => {
          const li = createReportListItem(report, "text");
          textReportsList.appendChild(li);
        });
    }

    // Update HTML reports
    const htmlReportsList = document.getElementById("html-reports");
    htmlReportsList.innerHTML = "";

    if (reports.html.length === 0) {
      htmlReportsList.innerHTML =
        '<li class="no-reports">No HTML reports available</li>';
    } else {
      reports.html
        .sort()
        .reverse()
        .forEach((report) => {
          const li = createReportListItem(report, "html");
          htmlReportsList.appendChild(li);
        });
    }

    // Update CSV reports
    const csvReportsList = document.getElementById("csv-reports");
    csvReportsList.innerHTML = "";

    if (reports.csv.length === 0) {
      csvReportsList.innerHTML =
        '<li class="no-reports">No CSV reports available</li>';
    } else {
      reports.csv
        .sort()
        .reverse()
        .forEach((report) => {
          const li = createReportListItem(report, "csv");
          csvReportsList.appendChild(li);
        });
    }
  }

  function createReportListItem(report, type) {
    const li = document.createElement("li");

    const link = document.createElement("a");
    link.href = `/report/${report}`;
    link.target = "_blank";

    // Add icon based on report type
    const icon = document.createElement("i");
    if (type === "text") {
      icon.className = "fas fa-file-alt";
    } else if (type === "html") {
      icon.className = "fas fa-file-code";
    } else if (type === "csv") {
      icon.className = "fas fa-file-csv";
    }

    link.appendChild(icon);
    link.appendChild(document.createTextNode(report));

    // Extract date from filename (assuming format like domain_20250512_123456.txt)
    const dateMatch = report.match(/(\d{8}_\d{6})/);
    if (dateMatch) {
      const dateStr = dateMatch[1];
      const year = dateStr.substring(0, 4);
      const month = dateStr.substring(4, 6);
      const day = dateStr.substring(6, 8);
      const hour = dateStr.substring(9, 11);
      const minute = dateStr.substring(11, 13);

      const dateSpan = document.createElement("span");
      dateSpan.className = "report-date";
      dateSpan.textContent = `${year}-${month}-${day} ${hour}:${minute}`;
      link.appendChild(dateSpan);
    }

    li.appendChild(link);
    return li;
  }

  // Initialize the page
  updateReports();

  // Crawl limit slider
  const crawlLimitSlider = document.getElementById("crawl-limit");
  const crawlLimitValue = document.getElementById("crawl-limit-value");
  const noLimitCheckbox = document.getElementById("no-limit");

  // Update the crawl limit value display when the slider changes
  crawlLimitSlider.addEventListener("input", function () {
    crawlLimitValue.textContent = this.value;
  });

  // Disable/enable the slider when the "No limit" checkbox is toggled
  noLimitCheckbox.addEventListener("change", function () {
    crawlLimitSlider.disabled = this.checked;
    crawlLimitValue.style.opacity = this.checked ? "0.5" : "1";
  });

  // Auto-fill domain from URL
  const startUrlInput = document.getElementById("start-url");
  const allowedDomainInput = document.getElementById("allowed-domain");

  startUrlInput.addEventListener("blur", function () {
    if (this.value && !allowedDomainInput.value) {
      try {
        const url = new URL(this.value);
        allowedDomainInput.value = url.hostname;
      } catch (e) {
        // Invalid URL, do nothing
      }
    }
  });
});
