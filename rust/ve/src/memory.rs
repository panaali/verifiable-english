//! The binary's global memory budget. On 2026-10-10 and 2026-10-11 one `ve jsonl` search grew
//! to 91 GB and then 99 GB, and the kernel's OOM kill took every job sharing its scope with it.
//!
//! A counting allocator charges every live heap byte to one budget: `VE_RUST_MEMORY_LIMIT` bytes,
//! else `DEFAULT_LIMIT`. An allocation that would exceed the budget, or that the system refuses
//! (an address-space limit set by the caller), is not made. Instead the handler registered with
//! `on_exhausted` answers with ResourceLimit and ends the process. This is a resource bound: the
//! answer is a refusal, never a verdict. This module is the binary's only unsafe code. It forwards
//! every request to `System` unchanged.
#![allow(unsafe_code)]

use std::alloc::{GlobalAlloc, Layout, System};
use std::sync::OnceLock;
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering::Relaxed};

/// 8 GiB, `MAX_RUST_MEMORY_BYTES` in `ve/limits.py`.
pub const DEFAULT_LIMIT: usize = 8 << 30;
pub const VARIABLE: &str = "VE_RUST_MEMORY_LIMIT";

static LIMIT: AtomicUsize = AtomicUsize::new(DEFAULT_LIMIT);
static LIVE: AtomicUsize = AtomicUsize::new(0);
static ENDING: AtomicBool = AtomicBool::new(false);
static HANDLER: OnceLock<fn(usize) -> !> = OnceLock::new();

/// The allocator: `System`, with every live byte charged to the budget.
pub struct Budget;

/// Set the budget from `VE_RUST_MEMORY_LIMIT` (a positive decimal number of bytes).
pub fn configure() -> Result<(), String> {
    let Some(text) = std::env::var_os(VARIABLE) else { return Ok(()) };
    let limit = text.to_str()
        .filter(|t| !t.is_empty() && t.bytes().all(|b| b.is_ascii_digit()))
        .and_then(|t| t.parse::<usize>().ok())
        .filter(|n| *n > 0)
        .ok_or_else(|| format!("{VARIABLE} must be a positive number of bytes, not {text:?}"))?;
    LIMIT.store(limit, Relaxed);
    Ok(())
}

/// The handler called with the budget (in bytes) when an allocation cannot be made. It may
/// allocate: once it runs, the budget no longer applies, because the process is ending.
pub fn on_exhausted(handler: fn(usize) -> !) {
    let _ = HANDLER.set(handler);
}

/// The bytes an allocation of `size` occupies: the system allocator's chunk (glibc's 8-byte
/// header, rounded to 16, at least 32), so many small allocations are not undercounted.
fn chunk(size: usize) -> usize {
    size.saturating_add(8).next_multiple_of(16).max(32)
}

fn charge(size: usize) -> bool {
    if ENDING.load(Relaxed) {
        LIVE.fetch_add(size, Relaxed);
        return true;
    }
    let limit = LIMIT.load(Relaxed);
    LIVE.fetch_update(Relaxed, Relaxed, |live| live.checked_add(size).filter(|n| *n <= limit)).is_ok()
}

fn refund(size: usize) {
    LIVE.fetch_sub(size, Relaxed);
}

/// No allocation: the handler ends the process. With no handler, or if the handler's own
/// allocation fails, the result is null, and Rust aborts.
fn exhausted() -> *mut u8 {
    if ENDING.swap(true, Relaxed) {
        return std::ptr::null_mut();
    }
    match HANDLER.get() {
        Some(handler) => handler(LIMIT.load(Relaxed)),
        None => std::ptr::null_mut(),
    }
}

unsafe impl GlobalAlloc for Budget {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        if !charge(chunk(layout.size())) {
            return exhausted();
        }
        let pointer = unsafe { System.alloc(layout) };
        if pointer.is_null() {
            refund(chunk(layout.size()));
            return exhausted();
        }
        pointer
    }
    unsafe fn alloc_zeroed(&self, layout: Layout) -> *mut u8 {
        if !charge(chunk(layout.size())) {
            return exhausted();
        }
        let pointer = unsafe { System.alloc_zeroed(layout) };
        if pointer.is_null() {
            refund(chunk(layout.size()));
            return exhausted();
        }
        pointer
    }
    unsafe fn dealloc(&self, pointer: *mut u8, layout: Layout) {
        unsafe { System.dealloc(pointer, layout) };
        refund(chunk(layout.size()));
    }
    unsafe fn realloc(&self, pointer: *mut u8, layout: Layout, size: usize) -> *mut u8 {
        let (before, after) = (chunk(layout.size()), chunk(size));
        let growth = after.saturating_sub(before);
        if !charge(growth) {
            return exhausted();
        }
        let moved = unsafe { System.realloc(pointer, layout, size) };
        if moved.is_null() {
            refund(growth);
            return exhausted();
        }
        refund(before.saturating_sub(after));
        moved
    }
}

/// The budget in bytes.
pub fn limit() -> usize {
    LIMIT.load(Relaxed)
}
