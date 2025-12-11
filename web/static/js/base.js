const defaultConfig = {
  background_color: "#0f172a",
  surface_color: "#1e293b",
  text_color: "#f1f5f9",
  primary_action_color: "#3b82f6",
  secondary_action_color: "#334155",
  font_family: "Inter",
  font_size: 16,
  dashboard_title: "Network Automation Dashboard",
  subtitle_text: "Real-time monitoring and control center",
  total_devices_label: "Total Devices",
  active_automations_label: "Active Automations",
  success_rate_label: "Success Rate",
  pending_tasks_label: "Pending Tasks"
};

async function onConfigChange(config) {
  const baseSize = config.font_size || defaultConfig.font_size;
  const customFont = config.font_family || defaultConfig.font_family;
  const baseFontStack = '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
  const fontFamily = `${customFont}, ${baseFontStack}`;

  const appWrapper = document.getElementById('app-wrapper');
  appWrapper.style.background = config.background_color || defaultConfig.background_color;
  appWrapper.style.fontFamily = fontFamily;

  const surfaceElements = document.querySelectorAll('[style*="background: #1e293b"]');
  surfaceElements.forEach(el => {
    el.style.background = config.surface_color || defaultConfig.surface_color;
  });

  const titleElement = document.getElementById('dashboard-title');
  titleElement.textContent = config.dashboard_title || defaultConfig.dashboard_title;
  titleElement.style.color = config.text_color || defaultConfig.text_color;
  titleElement.style.fontSize = `${baseSize * 2}px`;

  const subtitleElement = document.getElementById('subtitle-text');
  subtitleElement.textContent = config.subtitle_text || defaultConfig.subtitle_text;
  subtitleElement.style.fontSize = `${baseSize}px`;

  const totalDevicesLabel = document.getElementById('total-devices-label');
  totalDevicesLabel.textContent = config.total_devices_label || defaultConfig.total_devices_label;
  totalDevicesLabel.style.fontSize = `${baseSize * 0.9}px`;

  const activeAutomationsLabel = document.getElementById('active-automations-label');
  activeAutomationsLabel.textContent = config.active_automations_label || defaultConfig.active_automations_label;
  activeAutomationsLabel.style.fontSize = `${baseSize * 0.9}px`;

  const successRateLabel = document.getElementById('success-rate-label');
  successRateLabel.textContent = config.success_rate_label || defaultConfig.success_rate_label;
  successRateLabel.style.fontSize = `${baseSize * 0.9}px`;

  const pendingTasksLabel = document.getElementById('pending-tasks-label');
  pendingTasksLabel.textContent = config.pending_tasks_label || defaultConfig.pending_tasks_label;
  pendingTasksLabel.style.fontSize = `${baseSize * 0.9}px`;

  const primaryButtons = document.querySelectorAll('button[style*="#3b82f6"]');
  primaryButtons.forEach(btn => {
    const originalBg = config.primary_action_color || defaultConfig.primary_action_color;
    btn.style.background = originalBg;
    btn.onmouseover = function() { this.style.background = darkenColor(originalBg, 20); };
    btn.onmouseout = function() { this.style.background = originalBg; };
  });

  const secondaryButtons = document.querySelectorAll('button[style*="border: 1px solid #334155"]');
  secondaryButtons.forEach(btn => {
    const originalBg = config.surface_color || defaultConfig.surface_color;
    const borderColor = config.secondary_action_color || defaultConfig.secondary_action_color;
    btn.style.background = originalBg;
    btn.style.borderColor = borderColor;
    btn.onmouseover = function() { this.style.background = borderColor; };
    btn.onmouseout = function() { this.style.background = originalBg; };
  });
}

function darkenColor(hex, percent) {
  const num = parseInt(hex.slice(1), 16);
  const r = Math.max(0, ((num >> 16) * (100 - percent)) / 100);
  const g = Math.max(0, (((num >> 8) & 0x00FF) * (100 - percent)) / 100);
  const b = Math.max(0, ((num & 0x0000FF) * (100 - percent)) / 100);
  return `#${((1 << 24) + (Math.round(r) << 16) + (Math.round(g) << 8) + Math.round(b)).toString(16).slice(1)}`;
}

function mapToCapabilities(config) {
  return {
    recolorables: [
      {
        get: () => config.background_color || defaultConfig.background_color,
        set: (value) => {
          config.background_color = value;
          if (window.elementSdk) window.elementSdk.setConfig({ background_color: value });
        }
      },
      {
        get: () => config.surface_color || defaultConfig.surface_color,
        set: (value) => {
          config.surface_color = value;
          if (window.elementSdk) window.elementSdk.setConfig({ surface_color: value });
        }
      },
      {
        get: () => config.text_color || defaultConfig.text_color,
        set: (value) => {
          config.text_color = value;
          if (window.elementSdk) window.elementSdk.setConfig({ text_color: value });
        }
      },
      {
        get: () => config.primary_action_color || defaultConfig.primary_action_color,
        set: (value) => {
          config.primary_action_color = value;
          if (window.elementSdk) window.elementSdk.setConfig({ primary_action_color: value });
        }
      },
      {
        get: () => config.secondary_action_color || defaultConfig.secondary_action_color,
        set: (value) => {
          config.secondary_action_color = value;
          if (window.elementSdk) window.elementSdk.setConfig({ secondary_action_color: value });
        }
      }
    ],
    borderables: [],
    fontEditable: {
      get: () => config.font_family || defaultConfig.font_family,
      set: (value) => {
        config.font_family = value;
        if (window.elementSdk) window.elementSdk.setConfig({ font_family: value });
      }
    },
    fontSizeable: {
      get: () => config.font_size || defaultConfig.font_size,
      set: (value) => {
        config.font_size = value;
        if (window.elementSdk) window.elementSdk.setConfig({ font_size: value });
      }
    }
  };
}

function mapToEditPanelValues(config) {
  return new Map([
    ["dashboard_title", config.dashboard_title || defaultConfig.dashboard_title],
    ["subtitle_text", config.subtitle_text || defaultConfig.subtitle_text],
    ["total_devices_label", config.total_devices_label || defaultConfig.total_devices_label],
    ["active_automations_label", config.active_automations_label || defaultConfig.active_automations_label],
    ["success_rate_label", config.success_rate_label || defaultConfig.success_rate_label],
    ["pending_tasks_label", config.pending_tasks_label || defaultConfig.pending_tasks_label]
  ]);
}

if (window.elementSdk) {
  window.elementSdk.init({
    defaultConfig,
    onConfigChange,
    mapToCapabilities,
    mapToEditPanelValues
  });
}