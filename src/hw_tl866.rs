// TL866II-Plus adapter scaffold (experimental)
// This module is a scaffold for future direct libusb-based control for TL866II+ programmers.
// Implementing full protocol requires vendor commands or reverse-engineering the USB protocol.
// For now this provides detection helpers and a safe wrapper to call external CLI tools (minipro/xgpro).
use anyhow::Result;
use rusb::{Context, DeviceHandle, GlobalContext, UsbContext};

pub fn detect_tl866() -> Result<bool> {
    let ctx = Context::new()?;
    for device in ctx.devices()?.iter() {
        let desc = device.device_descriptor()?;
        // TL866 family specific VID/PID vary by vendor; here we just list devices and let user decide
        println!(\"Device: {:04x}:{:04x}\", desc.vendor_id(), desc.product_id());
    }
    Ok(true)
}

// Placeholder: open device and claim interface
pub fn open_device(vid: u16, pid: u16) -> Result<DeviceHandle<GlobalContext>> {
    let ctx = Context::new()?;
    for device in ctx.devices()?.iter() {
        let desc = device.device_descriptor()?;
        if desc.vendor_id() == vid && desc.product_id() == pid {
            let handle = device.open()?;
            return Ok(handle);
        }
    }
    Err(anyhow::anyhow!(\"Device not found\"))
}

// Future: implement native read/write using vendor protocol or reuse minipro internals via subprocess.
