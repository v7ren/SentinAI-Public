package main

import "strings"

// rejectedPermissionTypes are tool permissions this bridge must never grant.
// The scan layer reads code from the request body and returns findings; it is
// not a coding agent and must not run shell or edit files.
var rejectedPermissionTypes = map[string]struct{}{
	"bash":  {},
	"shell": {},
	"edit":  {},
	"write": {},
}

// shouldRejectPermission reports whether an OpenCode permission request must be rejected.
func shouldRejectPermission(permType string) bool {
	key := strings.ToLower(strings.TrimSpace(permType))
	if key == "" {
		return false
	}
	_, ok := rejectedPermissionTypes[key]
	return ok
}
