const rejectedPermissionTypes = new Set(["bash", "shell", "edit", "write"]);

/** Whether an OpenCode permission request must be rejected (no shell / file edits). */
export function shouldRejectPermission(permType: string): boolean {
  const key = permType.trim().toLowerCase();
  if (!key) return false;
  return rejectedPermissionTypes.has(key);
}
