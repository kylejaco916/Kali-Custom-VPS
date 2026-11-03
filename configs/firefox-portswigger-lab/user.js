// PortSwigger Web Security Academy & Local DevSecOps Lab Profile Configuration
// Proxy Mode: Primary Caido Proxy (127.0.0.1:8080) - switchable via `proxy-toggle`
user_pref("network.proxy.type", 1);
user_pref("network.proxy.http", "127.0.0.1");
user_pref("network.proxy.http_port", 8080);
user_pref("network.proxy.ssl", "127.0.0.1");
user_pref("network.proxy.ssl_port", 8080);
user_pref("network.proxy.share_proxy_settings", true);
user_pref("network.proxy.no_proxies_on", "");
user_pref("network.proxy.allow_hijacking_localhost", true);

// Enable Container Tabs (Contextual Identity) out-of-the-box for Multi-Role Auth Testing
user_pref("privacy.userContext.enabled", true);
user_pref("privacy.userContext.ui.enabled", true);
user_pref("privacy.userContext.longPressBehavior", 2);

// Trust & TLS Interception Hygiene (prevent OCSP/Pinning blocks on MITM certs)
user_pref("security.enterprise_roots.enabled", true);
user_pref("security.OCSP.enabled", 0);
user_pref("security.ssl.enable_ocsp_stapling", false);
user_pref("security.cert_pinning.enforcement_level", 0);
user_pref("network.stricttransportsecurity.preloadlist", false);
user_pref("dom.security.https_only_mode", false);

// Silence Firefox background noise in Caido/ZAP proxy history
user_pref("network.captive-portal-service.enabled", false);
user_pref("network.connectivity-service.enabled", false);
user_pref("browser.safebrowsing.malware.enabled", false);
user_pref("browser.safebrowsing.phishing.enabled", false);
user_pref("browser.safebrowsing.downloads.enabled", false);
user_pref("datareporting.healthreport.uploadEnabled", false);
user_pref("toolkit.telemetry.enabled", false);
user_pref("app.shield.optoutstudies.enabled", false);
user_pref("browser.shell.checkDefaultBrowser", false);
user_pref("browser.startup.homepage", "https://portswigger.net/web-security/all-labs");
user_pref("browser.startup.page", 1);
