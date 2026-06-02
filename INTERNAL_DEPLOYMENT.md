# Internal Streamlit Deployment

GitHub is not required for internal deployment. Host this folder on an internal Windows server, VM, or always-on workstation that stakeholders can reach on the corporate network or VPN.

## Option A: Temporary Share From This Machine

The app is currently running locally on port `8765`.

Stakeholder URL on the same network:

```text
http://192.168.1.107:8765/
```

This only works while this machine is powered on, connected to the network, and the Streamlit process is running.

## Option B: Internal Server / VM

1. Copy the deployment package or this folder to the server.
2. Install Python 3.11 or newer on the server.
3. Open PowerShell in the dashboard folder.
4. Run:

```powershell
.\start_dashboard.ps1
```

5. Stakeholders can access:

```text
http://SERVER-NAME:8765/
```

or:

```text
http://SERVER-IP:8765/
```

## Firewall

If stakeholders cannot connect, ask IT to allow inbound TCP traffic to port `8765` on the server.

## Permanent URL

For a friendlier internal URL, ask IT to create a DNS name such as:

```text
http://chain-status-dashboard.company.internal/
```

and route it to the server on port `8765`.
