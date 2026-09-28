# app/keywords.py
from typing import List

CRITICAL_KEYWORDS_DICT = {
    
    # ============ INJECTION VULNERABILITIES ============
    
    # SQL Injection (Extended)
    "sql_injection": [
        # Query execution
        "execute(", "executemany(", "executeQuery(", "executeUpdate(",
        "query(", "raw(", "rawQuery(", "exec(", "sp_executesql",
        "mysqli_query", "mysql_query", "pg_query", "sqlite_query",
        "mssql_query", "oci_execute", "db2_exec", "sqlsrv_query",      
        
        # SQL Keywords
        "SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER",
        "TRUNCATE", "MERGE", "REPLACE", "WHERE", "ORDER BY", "GROUP BY",
        "HAVING", "UNION", "JOIN", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN",
        "EXEC", "EXECUTE", "xp_cmdshell", "OPENROWSET", "OPENDATASOURCE",
        
        # Prepared statements (vulnerable if misused)
        "prepare(", "statement", "cursor.execute", "cursor.executemany",
        "PreparedStatement", "CallableStatement", "SqlCommand", "SqlDataAdapter",
        "OleDbCommand", "OdbcCommand", "createQuery", "createNativeQuery",
        "createSQLQuery", "createStatement",
        
        # ORM potentially vulnerable methods
        "db.query", "db.execute", "db.raw", "Model.raw", "find_by_sql",
        "where(", "order(", "group(", "having(", "joins(",
        "select_raw", "whereRaw", "orderByRaw", "havingRaw",
        
        # String operations (concatenation risks)
        "String.format", "sprintf", "printf", "concatenation", "+", "||",
        "CONCAT", "concat", "f\"", "f'", "${", "interpolation",

        # SQL injection extensions
        "INFORMATION_SCHEMA", "sys.tables", "sys.columns",
        "pg_sleep", "WAITFOR DELAY", "BENCHMARK(",
        "LOAD_FILE(", "INTO OUTFILE", "INTO DUMPFILE",
        "EXTRACTVALUE(", "UPDATEXML(", "xmltype(",
        "stacked queries", "time-based", "error-based",
        "CAST(", "CONVERT(", "CHAR(", "ASCII(",
        "0x", "0b", "hex(", "unhex("
    ],
    
    # NoSQL Injection (Extended)
    "nosql_injection": [
        # MongoDB
        "find(", "findOne(", "findById(", "update(", "updateOne(", "updateMany(",
        "remove(", "deleteOne(", "deleteMany(", "aggregate(", "count(",
        "distinct(", "mapReduce(", "findAndModify(", "findOneAndUpdate(",
        "$where", "$ne", "$gt", "$gte", "$lt", "$lte", "$in", "$nin",
        "$regex", "$exists", "$type", "$mod", "$text", "$expr",
        "db.eval", "db.collection", "db.runCommand",
        
        # CouchDB
        "CouchDB", "nano", "_design", "_view", "emit(",
        
        # Redis
        "redis.eval", "redis.evalsha", "redis.get", "redis.set",
        "EVAL", "EVALSHA", "SCRIPT LOAD",
        
        # Cassandra
        "cassandra", "execute_async", "cql",
        
        # DynamoDB
        "dynamodb", "query", "scan", "ExpressionAttributeValues"
    ],
    
    # LDAP Injection (Extended)
    "ldap_injection": [
        "ldap_search", "ldap_bind", "ldap_connect", "ldap_read",
        "ldap_list", "ldap_compare", "ldap_add", "ldap_modify",
        "LdapConnection", "DirectorySearcher", "SearchRequest",
        "InitialDirContext", "DirContext.search", "LdapContext",
        "filter=", "searchFilter", "SearchFilter", "LDAPFilter",
        "|(", "&(", "!(", "*(", ")(", "cn=", "uid=", "ou=", "dc="
    ],
    
    # XPath Injection
    "xpath_injection": [
        "xpath", "XPath", "XPathExpression", "XPathNavigator",
        "selectNodes", "selectSingleNode", "evaluate", "compile",
        "//", "/*", "[", "]", "ancestor::", "descendant::",
        "xml.xpath", "lxml.xpath", "XPathFactory"
    ],
    
    # Command Injection (Extended)
    "command_injection": [
        # Python
        "os.system", "os.popen", "os.spawn", "os.exec", "os.execl",
        "os.execle", "os.execlp", "os.execv", "os.execve", "os.execvp",
        "subprocess.call", "subprocess.run", "subprocess.Popen",
        "subprocess.check_call", "subprocess.check_output",
        "commands.getoutput", "commands.getstatusoutput",
        
        # PHP
        "exec(", "system(", "shell_exec(", "passthru(", "popen(",
        "proc_open(", "pcntl_exec(", "backtick", "`",
        
        # Java
        "Runtime.getRuntime().exec", "ProcessBuilder", "Process",
        "ProcessImpl", "UNIXProcess", "ProcessEnvironment",
        
        # Node.js
        "child_process.exec", "child_process.execSync", "child_process.spawn",
        "child_process.execFile", "child_process.fork",
        
        # .NET
        "Process.Start", "ProcessStartInfo", "ShellExecute",
        "WinExec", "CreateProcess", "System.Diagnostics.Process",
        
        # Ruby
        "system(", "exec(", "spawn(", "IO.popen", "Open3",
        "%x", "Kernel.system", "Kernel.exec",
        
        # Shell commands
        "cmd.exe", "sh -c", "bash -c", "/bin/sh", "/bin/bash",
        "powershell", "pwsh", "cmd /c", "sh", "zsh", "ksh",
        
        # Command separators
        ";", "&&", "||", "|", "&", "\n", "`", "$("
    ],
    
    # Code Injection (Extended)
    "code_injection": [
        # Python
        "eval(", "exec(", "compile(", "execfile(", "__import__",
        "importlib.import_module", "reload(", "input(", "raw_input(",
        
        # JavaScript
        "eval(", "Function(", "setTimeout(", "setInterval(",
        "new Function", "eval.call", "Function.constructor",
        "GeneratorFunction", "AsyncFunction",
        
        # Node.js
        "vm.runInContext", "vm.runInNewContext", "vm.runInThisContext",
        "require(", "import(", "module.require",
        
        # PHP
        "eval(", "assert(", "create_function(", "preg_replace /e",
        "call_user_func", "call_user_func_array", "array_map",
        
        # Java
        "ScriptEngine", "ScriptEngineManager", "Reflection",
        "invoke", "getDeclaredMethod", "getMethod", "newInstance",
        "Class.forName", "ClassLoader.loadClass",
        
        # .NET
        "CodeDom", "CSharpCodeProvider", "CompileAssemblyFromSource",
        "Reflection.Emit", "DynamicMethod", "ILGenerator",
        
        # Ruby
        "eval", "instance_eval", "class_eval", "module_eval",
        "binding.eval", "Kernel.eval", "send", "public_send"
    ],
    
    # Expression Language Injection
    "el_injection": [
        "EL", "OGNL", "MVEL", "SpEL", "Unified EL",
        "${", "#{", "%{", "@{", "T(", "new(",
        "getClass", "forName", "getRuntime", "ProcessBuilder"
    ],
    
    # Template Injection (Extended)
    "template_injection": [
        # Python
        "render_template_string", "Template(", "Jinja2", "Mako",
        "Cheetah", "Genshi", "Django.template", "string.Template",
        
        # Java
        "Velocity", "Freemarker", "Thymeleaf", "JSP", "JSTL",
        "Pebble", "Handlebars", "Mustache",
        
        # PHP
        "Twig", "Smarty", "Blade", "Plates",
        
        # JavaScript
        "Handlebars", "Mustache", "EJS", "Pug", "Jade",
        "Nunjucks", "Dust", "doT",
        
        # Template syntax
        "{{", "}}", "{%", "%}", "<%", "%>", "${", "}",
        "[[", "]]", "{#", "#}", "<#", "#>",
        
        # Methods
        "render", "compile", "evaluate", "process", "execute"
    ],
    
    # XML/XXE Injection (Extended)
    "xxe_injection": [
        # Python
        "xml.etree.ElementTree", "xml.dom.minidom", "xml.sax",
        "lxml.etree", "pulldom", "xmlrpclib", "defusedxml",
        
        # Java
        "DocumentBuilder", "DocumentBuilderFactory", "SAXParser",
        "SAXParserFactory", "XMLReader", "XMLInputFactory",
        "Transformer", "TransformerFactory", "SchemaFactory",
        "Validator", "XPathFactory",
        
        # .NET
        "XmlDocument", "XmlTextReader", "XmlReader", "XPathNavigator",
        "XslCompiledTransform", "DataSet.ReadXml",
        
        # PHP
        "simplexml_load_string", "simplexml_load_file", "DOMDocument",
        "XMLReader", "xml_parse",
        
        # XML entities
        "<!ENTITY", "<!DOCTYPE", "SYSTEM", "PUBLIC", "ENTITY",
        "file://", "http://", "ftp://", "gopher://", "expect://",
        
        # Settings
        "setFeature", "setAttribute", "setProperty",
        "FEATURE_SECURE_PROCESSING", "EXTERNAL_GENERAL_ENTITIES",
        "EXTERNAL_PARAMETER_ENTITIES", "LOAD_EXTERNAL_DTD",

        # XXE extensions
        "resolve-dtd-uris",
        "is-supporting-external-entities",
        "http://xml.org/sax/features/external-general-entities",
        "http://xml.org/sax/features/external-parameter-entities",
        "http://apache.org/xml/features/disallow-doctype-decl",
        "libxml2", "libxml_disable_entity_loader",
        "nokogiri", "Nokogiri::XML",
        "etree.parse", "etree.fromstring"
    ],
    
    # HTML Injection
    "html_injection": [
        "innerHTML", "outerHTML", "insertAdjacentHTML",
        "document.write", "document.writeln", "write(",
        "DOMParser", "createContextualFragment"
    ],
    
    # CSV Injection
    "csv_injection": [
        "csv.writer", "to_csv", "write_csv", "CsvWriter",
        "writerow", "DictWriter",
        "=CMD(", "=HYPERLINK(", "=IMPORTXML(",
        "=IMPORTDATA(", "=IMPORTFEED(", "=IMPORTHTML(",
        "+cmd|", "@SUM(", "-2+3+cmd|",
        "=DDE(", "=INDIRECT(",
    ],
    
    # Server-Side Includes (SSI) Injection
    "ssi_injection": [
        "<!--#exec", "<!--#include", "<!--#echo", "<!--#config",
        "<!--#set", "<!--#if", "<!--#elif", "<!--#else", "<!--#endif"
    ],
    
    # ============ CROSS-SITE SCRIPTING (XSS) ============
    
    "xss": [
        # DOM manipulation
        "innerHTML", "outerHTML", "insertAdjacentHTML",
        "document.write", "document.writeln", "write(",
        "textContent", "innerText", "outerText",
        
        # JavaScript execution
        "eval(", "setTimeout", "setInterval", "Function(",
        "new Function", "execScript", "setImmediate",
        
        # Framework-specific
        "dangerouslySetInnerHTML", "v-html", "ng-bind-html",
        "[innerHTML]", "bypassSecurityTrust", "sanitize",
        
        # Server-side output
        "echo", "print", "printf", "print_r", "var_dump",
        "response.write", "Response.Write", "out.println",
        "render", "render_template", "<%=", "<?=",
        
        # Event handlers
        "onerror=", "onload=", "onclick=", "onmouseover=",
        "onfocus=", "onblur=", "onchange=", "onsubmit=",
        
        # Protocols
        "javascript:", "data:", "vbscript:", "about:",
        
        # Encoding
        "fromCharCode", "String.fromCharCode", "unescape",
        "decodeURI", "decodeURIComponent", "atob", "btoa",
        
        # Tags
        "<script>", "<iframe>", "<object>", "<embed>",
        "<img", "<svg", "<video", "<audio", "<link", "<style",

        # XSS extensions
        "srcdoc=", "sandbox=", "allowscriptaccess",
        "xlink:href", "xml:base", "formaction=",
        "<details", "<marquee", "<isindex",
        "autofocus", "onfocusin=", "onpointerover=",
        "expression(", "-moz-binding", "behavior:",
        "document.domain", "document.baseURI",
        "location.hash", "location.search",
        "postMessage", "addEventListener"
    ],
    
    # ============ AUTHENTICATION & SESSION ============
    
    "authentication": [
        # Authentication functions
        "authenticate", "login", "signin", "sign_in", "logon",
        "verify", "validate", "check_password", "compare_password",
        
        # Session management
        "session", "Session", "HttpSession", "session_start",
        "session_regenerate_id", "session_destroy", "setcookie",
        "Cookie", "Cookies", "document.cookie",
        
        # Tokens
        "token", "jwt", "bearer", "oauth", "api_key", "access_token",
        "refresh_token", "csrf_token", "authenticity_token",
        
        # Password handling
        "password", "passwd", "pwd", "pass", "secret",
        "credential", "auth", "authentication",
        
        # Weak hashing
        "md5", "MD5", "sha1", "SHA1", "crc32", "adler32",
        
        # Hardcoded credentials
        "hardcoded", "hardcode", "default_password", "admin",
        "root", "password123", "admin123", "test", "demo",

        # Authentication extensions
        "compare_digest", "constant_time_compare",
        "brute_force", "account_lockout", "max_attempts",
        "MFA", "2FA", "TOTP", "HOTP", "OTP",
        "remember_me", "persistent_login",
        "forgot_password", "reset_password", "password_reset",
        "security_question", "backup_code"
    ],
    
    "authorization": [
        "authorize", "isAuthorized", "hasRole", "hasPermission",
        "canAccess", "checkAccess", "requireRole", "requirePermission",
        "admin", "superuser", "root", "sudo", "privilege",
        "ACL", "RBAC", "permission", "role", "grant", "deny",
        "@PreAuthorize", "@Secured", "@RolesAllowed",
        "authorize!", "can?", "cannot?", "ability"
    ],
    
    # ============ CRYPTOGRAPHY ============
    
    "cryptography": [
        # Weak algorithms
        "md5", "MD5", "sha1", "SHA1", "des", "DES", "3des", "3DES",
        "rc2", "RC2", "rc4", "RC4", "rc5", "RC5", "blowfish",
        
        # Weak modes
        "ECB", "ecb", "CBC", "cbc", "OFB", "ofb", "CFB", "cfb",
        
        # Encryption/Decryption
        "encrypt", "decrypt", "cipher", "Cipher", "decipher",
        "AES", "RSA", "ECC", "DSA", "ECDSA", "ElGamal",
        
        # Hashing
        "hash", "Hash", "digest", "HMAC", "hmac",
        "sha256", "SHA256", "sha512", "SHA512",
        "bcrypt", "scrypt", "argon2", "PBKDF2",
        
        # Random number generation
        "random", "Random", "rand", "srand", "mt_rand",
        "Math.random", "Random(", "SecureRandom", "CryptoRandom",
        "urandom", "SystemRandom", "secrets",
        
        # Keys and certificates
        "private_key", "public_key", "secret_key", "api_key",
        "certificate", "cert", "key", "pem", "der", "p12", "pfx",
        
        # SSL/TLS
        "ssl", "SSL", "tls", "TLS", "https", "HTTPS",
        "SSLContext", "TrustManager", "HostnameVerifier",
        "verify=False", "verify_mode", "check_hostname",

        # Crypto extensions
        "IV", "iv", "nonce", "salt",
        "hardcoded_key", "static_key", "fixed_iv",
        "padding", "PKCS1", "PKCS5", "PKCS7",
        "NoPadding", "ZeroPadding",
        "PRNG", "weak_random", "predictable",
        "timing_attack", "constant_time", "hmac_compare",
        "compare_digest", "secrets.compare_digest",
        "key_derivation", "KDF", "HKDF"
    ],

    # ============ PATH TRAVERSAL ============

    "path_traversal": [
        "../", "..\\", "%2e%2e%2f", "%2e%2e/", "..%2f", "%2e%2e%5c",
        "....//", "....\\\\", "%252e%252e", "..;/",
        "path.join", "os.path.join", "Path.Combine",
        "realpath", "canonicalize", "normalize",
        "getCanonicalPath", "getAbsolutePath",
        "basename", "dirname", "pathinfo",
        "WEB-INF", "META-INF", "/etc/passwd", "/etc/shadow",
        "C:\\Windows\\", "C:\\boot.ini", "web.config",
        "../../../../", "..%252f", "..%c0%af", "..%c1%9c"
    ],

    # ============ PROTOTYPE POLLUTION ============

    "prototype_pollution": [
        "__proto__", "prototype", "constructor",
        "Object.assign(", "_.merge(", "_.extend(", "_.defaultsDeep(",
        "jQuery.extend(", "merge(", "extend(", "defaults(",
        "deepMerge", "deepExtend", "deepAssign",
        "hasOwnProperty", "Object.keys", "Object.entries",
        "JSON.parse", "qs.parse", "querystring.parse",
        "body-parser", "express-fileupload"
    ],

    # ============ HTTP REQUEST SMUGGLING ============

    "http_smuggling": [
        "Transfer-Encoding", "Content-Length", "chunked",
        "TE:", "CL:", "TE.CL", "CL.TE", "CL.CL",
        "keep-alive", "Connection:", "Upgrade:",
        "HTTP/1.1", "HTTP/2", "h2c",
        "proxy_pass", "upstream", "reverse_proxy",
        "haproxy", "nginx", "apache"
    ],

    # ============ DNS & SUBDOMAIN TAKEOVER ============

    "dns_subdomain": [
        "CNAME", "A record", "DNS", "subdomain",
        "dns.resolve", "dns.lookup", "getaddrinfo",
        "gethostbyname", "socket.gethostbyname",
        "InetAddress.getByName", "Dns.GetHostEntry",
        "nslookup", "dig", "host",
        "dangling", "takeover", "unclaimed"
    ],

    # ============ SUPPLY CHAIN / DEPENDENCY CONFUSION ============

    "supply_chain": [
        "requirements.txt", "package.json", "Gemfile",
        "pom.xml", "build.gradle", "go.mod", "Cargo.toml",
        "npm install", "pip install", "gem install",
        "setup.py", "pyproject.toml",
        "dependency", "package", "module", "import",
        "registry", "artifactory", "nexus", "pypi",
        "npmjs", "unpkg", "jsdelivr", "cdnjs"
    ],

    # ============ FILE OPERATIONS ============

    "file_operations": [
        # File reading
        "open(", "file(", "read(", "readfile(", "fopen(", "fread(",
        "file_get_contents", "readFile", "readFileSync",
        "FileInputStream", "FileReader", "BufferedReader",
        "File.ReadAllText", "File.ReadAllBytes", "StreamReader",
        
        # File writing
        "write(", "writefile(", "fwrite(", "file_put_contents",
        "writeFile", "writeFileSync", "FileOutputStream",
        "FileWriter", "BufferedWriter", "File.WriteAllText",
        "File.WriteAllBytes", "StreamWriter",
        
        # File inclusion
        "include(", "require(", "include_once", "require_once",
        "import", "load", "loadfile", "source",
        
        # File upload
        "upload", "move_uploaded_file", "copy(", "rename(",
        "MultipartFile", "InputStream", "OutputStream",
        "HttpPostedFile", "IFormFile", "upload_file",
        
        # Directory operations
        "scandir", "listdir", "readdir", "opendir", "glob",
        "walk", "os.walk", "Directory.GetFiles", "DirectoryInfo",
        "mkdir", "rmdir", "unlink", "delete", "remove",
        
        # Path operations
        "path", "Path", "pathname", "filename", "filepath",
        "../", "..\\", "..", "~", "%2e%2e", "....//",
        "Path.Combine", "path.join", "File.separator",
        
        # File permissions
        "chmod", "chown", "chgrp", "umask", "setfacl",
        
        # Dangerous extensions
        ".php", ".jsp", ".asp", ".aspx", ".exe", ".sh",
        ".bat", ".cmd", ".ps1", ".py", ".rb", ".pl",
        ".cgi", ".dll", ".so", ".dylib",

        # File operations extensions
        "zipslip", "ZipSlip",
        "symlink", "os.symlink", "os.readlink",
        "hardlink", "os.link",
        "tempfile", "NamedTemporaryFile", "mkstemp", "tmpnam",
        "/tmp/", "predictable_filename",
        "content-disposition", "Content-Disposition"
    ],
    
    # ============ NETWORK & SSRF ============
    
    "network_ssrf": [
        # HTTP requests
        "requests.get", "requests.post", "requests.put", "requests.delete",
        "urllib.request", "urllib.urlopen", "urllib2", "httplib",
        "http.client", "curl", "curl_exec", "curl_init",
        "file_get_contents", "fopen", "fsockopen",
        
        # JavaScript/Node.js
        "fetch(", "axios", "XMLHttpRequest", "$.ajax", "$.get", "$.post",
        "http.get", "http.request", "https.get", "https.request",
        
        # Java
        "HttpClient", "HttpURLConnection", "URL.openConnection",
        "URL.openStream", "HttpRequest", "RestTemplate",
        
        # .NET
        "WebClient", "HttpClient", "WebRequest", "HttpWebRequest",
        "RestSharp", "HttpRequestMessage",
        
        # Internal/Private IPs
        "localhost", "127.0.0.1", "0.0.0.0", "::1",
        "10.", "172.16.", "192.168.", "169.254.169.254",
        "metadata", "internal", "private", "local",
        
        # Protocols
        "file://", "dict://", "ftp://", "gopher://", "ldap://",
        "tftp://", "jar://", "netdoc://", "mailto:",

        # SSRF bypass / metadata extensions
        "0177.0.0.1", "0x7f000001", "2130706433",
        "[::]", "[::1]",
        "metadata.google.internal", "computeMetadata",
        "instance-data", "169.254.170.2",
        "IMDSv1", "IMDSv2", "X-aws-ec2-metadata-token",
        "allow_redirects=True", "http.followRedirects",
        "maxRedirects", "followAllRedirects"
    ],
    
    "socket_operations": [
        "socket", "Socket", "ServerSocket", "DatagramSocket",
        "connect", "bind", "listen", "accept", "send", "recv",
        "sendto", "recvfrom", "TcpClient", "TcpListener",
        "UdpClient", "NetworkStream", "socket.socket"
    ],
    
    # ============ DESERIALIZATION ============
    
    "deserialization": [
        # Python
        "pickle.loads", "pickle.load", "cPickle", "dill",
        "shelve", "yaml.load", "yaml.unsafe_load",
        "marshal.loads", "marshal.load",
        
        # Java
        "ObjectInputStream", "readObject", "readUnshared",
        "XMLDecoder", "readResolve", "readExternal",
        "XStream", "fromXML", "Serializable",
        
        # .NET
        "BinaryFormatter", "SoapFormatter", "LosFormatter",
        "ObjectStateFormatter", "NetDataContractSerializer",
        "JsonConvert.DeserializeObject", "JavaScriptSerializer",
        
        # PHP
        "unserialize(", "serialize(", "__wakeup", "__destruct",
        "__toString", "Phar", "phar://",
        
        # Ruby
        "Marshal.load", "Marshal.restore", "Oj.load",
        "YAML.load", "Psych.load",
        
        # JavaScript/Node.js
        "JSON.parse", "eval(", "Function(", "vm.runInContext",
        "node-serialize", "serialize-javascript",

        # Deserialization extensions
        "gadget", "gadget chain", "ysoserial",
        "CommonsCollections", "Spring1", "Hibernate1",
        "readClassDescriptor", "resolveClass",
        "enableDefaultTyping", "ObjectMapper",
        "JsonTypeInfo", "@type", "autoType",
        "fastjson", "jackson", "gson",
        "Kryo", "Hessian", "AMF", "JMX"
    ],
    
    # ============ XML/XPATH ============
    
    "xml_processing": [
        "xml", "XML", "xpath", "XPath", "xslt", "XSLT",
        "xquery", "XQuery", "dtd", "DTD", "schema", "XSD",
        "parseXML", "loadXML", "fromstring", "parse",
        "XMLParser", "DOMParser", "SAXParser"
    ],
    
    # ============ REGEX & REDOS ============
    
    "regex": [
        # Python
        "re.compile", "re.match", "re.search", "re.findall",
        "re.finditer", "re.sub", "re.split",
        
        # Java
        "Pattern.compile", "Pattern.matches", "Matcher",
        
        # JavaScript
        "RegExp(", "new RegExp", ".match(", ".search(",
        ".replace(", ".split(", "test(",
        
        # PHP
        "preg_match", "preg_match_all", "preg_replace",
        "preg_split", "preg_grep", "ereg", "eregi",
        
        # .NET
        "Regex(", "Regex.Match", "Regex.IsMatch", "Regex.Replace",
        
        # Dangerous patterns (ReDoS)
        "(.*)*", "(a+)+", "(a|a)*", "(a|ab)*", "(a*)*",
        "([a-zA-Z]+)*", "(\\w+)*", "(\\d+)*"
    ],
    
    # ============ INFORMATION DISCLOSURE ============
    
    "info_disclosure": [
        # Error messages
        "printStackTrace", "print_r", "var_dump", "var_export",
        "debug_backtrace", "debug_print_backtrace",
        "console.log", "console.error", "console.trace",
        "Exception.getMessage", "Exception.getStackTrace",
        "Throwable.printStackTrace", "error_log", "trigger_error",
        
        # Debug/Info functions
        "phpinfo", "sys.path", "os.environ", "process.env",
        "getenv", "ENV", "System.getenv", "Environment.GetEnvironmentVariable",
        "debug", "DEBUG", "trace", "TRACE", "verbose",
        
        # Sensitive data
        "password", "passwd", "pwd", "secret", "token",
        "api_key", "apikey", "private_key", "access_token",
        "credit_card", "ssn", "social_security",
        
        # Stack traces
        "stack_trace", "backtrace", "callstack", "stacktrace",
        "Error.stack", "Exception.StackTrace"
    ],
    
    # ============ RACE CONDITIONS & CONCURRENCY ============
    
    "concurrency": [
        # Python
        "threading", "Thread(", "multiprocessing", "Process(",
        "Queue", "Lock", "RLock", "Semaphore", "Event",
        "async", "await", "asyncio", "concurrent.futures",
        
        # Java
        "Thread", "Runnable", "Callable", "ExecutorService",
        "Future", "CompletableFuture", "synchronized",
        "Lock", "ReentrantLock", "Semaphore", "CountDownLatch",
        "CyclicBarrier", "volatile", "atomic",
        
        # JavaScript
        "Promise", "async", "await", "setTimeout", "setInterval",
        "Worker", "SharedArrayBuffer", "Atomics",
        
        # .NET
        "Thread", "Task", "async", "await", "lock",
        "Monitor", "Mutex", "Semaphore", "ManualResetEvent",
        
        # Ruby
        "Thread.new", "Mutex", "ConditionVariable", "Queue",
        
        # TOCTOU
        "access(", "stat(", "lstat(", "File.exists",
        "os.path.exists", "File.Exists", "is_file", "is_dir"
    ],
    
    # ============ MEMORY & BUFFER ============
    
    "memory_buffer": [
        # Buffer operations
        "strcpy", "strcat", "sprintf", "vsprintf", "gets",
        "scanf", "memcpy", "memmove", "strncpy", "strncat",
        "Buffer", "ByteBuffer", "malloc", "calloc", "realloc",
        "alloca", "VirtualAlloc", "HeapAlloc",
        
        # Memory operations
        "free", "delete", "delete[]", "HeapFree", "VirtualFree",
        "pointer", "reference", "dereference", "nullptr",
        
        # Unsafe operations
        "unsafe", "Unsafe", "sun.misc.Unsafe", "Marshal",
        "IntPtr", "UIntPtr", "GCHandle"
    ],
    
    # ============ LDAP ============
    
    "ldap": [
        "ldap", "LDAP", "DirectoryEntry", "DirectorySearcher",
        "LdapConnection", "InitialDirContext", "DirContext",
        "ldap_bind", "ldap_search", "ldap_connect", "ldap_read"
    ],
    
    # ============ LOGGING ============
    
    "logging": [
        "log", "logger", "logging", "Log", "Logger",
        "log4j", "logback", "slf4j", "NLog", "Serilog",
        "winston", "bunyan", "pino", "console",
        "syslog", "rsyslog", "journald",
        "write_log", "error_log", "access_log"
    ],
    
    # ============ FRAMEWORKS & LIBRARIES ============
    
    "frameworks": [
        # Python
        "flask", "django", "fastapi", "tornado", "pyramid",
        "bottle", "cherrypy", "web2py", "turbogears",
        
        # JavaScript/Node.js
        "express", "koa", "hapi", "nest", "fastify",
        "restify", "sails", "meteor", "next", "nuxt",
        
        # Java
        "spring", "struts", "play", "grails", "vaadin",
        "jsf", "wicket", "tapestry", "gwt",
        
        # PHP
        "laravel", "symfony", "codeigniter", "cakephp",
        "yii", "zend", "slim", "lumen", "phalcon",
        
        # Ruby
        "rails", "sinatra", "padrino", "hanami", "grape",
        
        # .NET
        "asp.net", "mvc", "webapi", "wcf", "nancy",
        "servicestack", "blazor",
        
        # Go
        "gin", "echo", "fiber", "beego", "revel"
    ],
    
    # ============ DATABASE ============
    
    "database": [
        # Connections
        "connect", "connection", "cursor", "session",
        "Connection", "DataSource", "ConnectionPool",
        
        # SQL databases
        "mysql", "MySQL", "mysqli", "PDO", "SQLite",
        "PostgreSQL", "psycopg2", "pg", "MSSQL", "sqlserver",
        "Oracle", "oci", "DB2", "Sybase",
        
        # ORMs
        "SQLAlchemy", "Django ORM", "Hibernate", "Entity Framework",
        "Sequelize", "TypeORM", "Prisma", "ActiveRecord",
        "Doctrine", "Eloquent", "GORM",
        
        # NoSQL
        "MongoDB", "mongo", "mongoose", "Redis", "redis",
        "Cassandra", "CouchDB", "DynamoDB", "Neo4j",
        "Elasticsearch", "Solr"
    ],
    
    # ============ API & WEB ============
    
    "api_web": [
        # Routes/Endpoints
        "@app.route", "@route", "@RequestMapping", "@GetMapping",
        "@PostMapping", "@PutMapping", "@DeleteMapping", "@PatchMapping",
        "@api_view", "@action", "router.get", "router.post",
        "app.get", "app.post", "app.put", "app.delete", "app.patch",
        "Route(", "endpoint", "api/", "/v1/", "/v2/", "/api/",
        
        # HTTP methods
        "GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS",
        
        # Request handling
        "request", "Request", "HttpServletRequest", "HttpRequest",
        "req.body", "req.query", "req.params", "req.headers",
        "req.cookies", "request.form", "request.args",
        
        # Response handling
        "response", "Response", "HttpServletResponse", "HttpResponse",
        "res.send", "res.json", "res.render", "response.write",
        
        # CORS
        "CORS", "Access-Control-Allow-Origin", "Access-Control-Allow-Methods",
        "Access-Control-Allow-Headers", "Access-Control-Allow-Credentials",
        
        # REST
        "REST", "RESTful", "GraphQL", "gRPC", "SOAP", "WebSocket"
    ],
    
    # ============ INPUT SOURCES ============
    
    "input_sources": [
        # General
        "input", "user_input", "userinput", "data", "payload",
        
        # Web
        "request", "params", "query", "body", "form",
        "headers", "cookies", "cookie", "session",
        "$_GET", "$_POST", "$_REQUEST", "$_COOKIE", "$_SERVER",
        "$_FILES", "$_ENV", "$_SESSION",
        "req.body", "req.query", "req.params", "req.headers",
        "request.form", "request.args", "request.values",
        "request.json", "request.data", "request.files",
        
        # Java
        "HttpServletRequest", "getParameter", "getParameterValues",
        "getHeader", "getHeaders", "getCookies", "getInputStream",
        "getReader", "getPart", "getParts",
        
        # .NET
        "Request.Form", "Request.QueryString", "Request.Cookies",
        "Request.Headers", "Request.Body", "Request.Files",
        
        # Command line
        "argv", "args", "arguments", "sys.argv", "process.argv",
        "ARGV", "$*", "$@", "getopt", "argparse",
        
        # Environment
        "environ", "environment", "env", "getenv", "os.environ",
        "process.env", "System.getenv", "ENV",
        
        # Files
        "stdin", "STDIN", "System.in", "Console.ReadLine",
        "input(", "raw_input(", "gets(", "scanf("
    ],
    
    # ============ OUTPUT SINKS ============
    
    "output_sinks": [
        # Display
        "echo", "print", "printf", "println", "puts",
        "console.log", "Console.WriteLine", "System.out.println",
        "response.write", "Response.Write", "out.println",
        
        # Rendering
        "render", "render_template", "render_to_response",
        "render_to_string", "display", "show", "view",
        
        # Files
        "write", "writeln", "fwrite", "file_put_contents",
        "writeFile", "File.WriteAllText", "FileWriter"
    ],
    
    # ============ SECURITY HEADERS ============
    
    "security_headers": [
        "Content-Security-Policy", "CSP", "X-Frame-Options",
        "X-XSS-Protection", "X-Content-Type-Options",
        "Strict-Transport-Security", "HSTS",
        "Access-Control-Allow-Origin", "CORS",
        "X-Permitted-Cross-Domain-Policies",
        "Referrer-Policy", "Feature-Policy", "Permissions-Policy",
        "Cross-Origin-Embedder-Policy", "Cross-Origin-Opener-Policy",
        "Cross-Origin-Resource-Policy"
    ],
    
    # ============ COOKIES & SESSIONS ============
    
    "cookies_sessions": [
        "cookie", "Cookie", "setCookie", "setcookie",
        "document.cookie", "HttpCookie", "Set-Cookie",
        "Secure", "HttpOnly", "SameSite", "Domain", "Path",
        "session", "Session", "session_start", "session_id",
        "session_regenerate_id", "session_destroy",
        "HttpSession", "SessionState", "express-session"
    ],
    
    # ============ DANGEROUS FUNCTIONS ============
    
    "dangerous_functions": [
        # PHP
        "assert", "create_function", "extract", "parse_str",
        "preg_replace /e", "call_user_func", "call_user_func_array",
        "register_shutdown_function", "register_tick_function",
        "unlink", "rmdir", "chmod", "chown", "chgrp",
        "dl(", "putenv", "ini_set", "set_time_limit",
        "mail(", "mb_send_mail", "error_reporting",
        
        # Python
        "__import__", "importlib", "reload", "compile",
        "getattr", "setattr", "delattr", "hasattr",
        
        # JavaScript
        "eval", "Function", "setTimeout", "setInterval",
        "execScript", "setImmediate",
        
        # System
        "system", "exec", "shell_exec", "passthru", "popen"
    ],
    
    # ============ REFLECTION & DYNAMIC CODE ============
    
    "reflection": [
        # Python
        "getattr", "setattr", "hasattr", "delattr",
        "__import__", "importlib", "exec", "eval",
        "vars", "dir", "globals", "locals",
        
        # Java
        "Reflection", "Class.forName", "getDeclaredMethod",
        "getMethod", "invoke", "newInstance", "getDeclaredField",
        "getField", "setAccessible", "ClassLoader",
        
        # .NET
        "Reflection", "Type.GetType", "Activator.CreateInstance",
        "Assembly.Load", "MethodInfo.Invoke", "GetMethod",
        "GetField", "GetProperty",
        
        # JavaScript
        "Reflect", "Proxy", "Object.defineProperty",
        "Object.getOwnPropertyDescriptor", "__proto__",
        "constructor", "prototype"
    ],
    
    # ============ CLOUD & CONTAINERS ============
    
    "cloud_containers": [
        # AWS
        "aws", "boto3", "s3", "ec2", "lambda", "dynamodb",
        "iam", "sts", "secretsmanager", "ssm",
        
        # Azure
        "azure", "az", "AzureAD", "KeyVault", "BlobStorage",
        
        # GCP
        "gcp", "google-cloud", "gcs", "bigquery", "pubsub",
        
        # Docker
        "docker", "Docker", "dockerfile", "Dockerfile",
        "container", "image", "volume", "network",
        
        # Kubernetes
        "kubernetes", "k8s", "kubectl", "pod", "deployment",
        "service", "configmap", "secret", "namespace"
    ],
    
    # ============ MOBILE ============
    
    "mobile": [
        # Android
        "android", "Activity", "Intent", "ContentProvider",
        "BroadcastReceiver", "Service", "WebView",
        "SharedPreferences", "SQLiteDatabase",
        
        # iOS
        "ios", "swift", "objective-c", "UIViewController",
        "NSUserDefaults", "Keychain", "CoreData", "WKWebView"
    ],
    
    # ============ PROTOCOLS ============
    
    "protocols": [
        "http://", "https://", "ftp://", "ftps://", "file://",
        "ssh://", "telnet://", "ldap://", "ldaps://",
        "smtp://", "pop3://", "imap://", "dict://",
        "gopher://", "tftp://", "jar://", "netdoc://",
        "mailto:", "data:", "javascript:", "vbscript:"
    ],
    
    # ============ BUSINESS LOGIC ============
    
    "business_logic": [
        "price", "amount", "quantity", "balance", "credit",
        "discount", "coupon", "voucher", "payment", "checkout",
        "transfer", "withdraw", "deposit", "refund",
        "admin", "administrator", "moderator", "superuser",
        "privilege", "permission", "role", "access_level"
    ],
    
    # ============ MASS ASSIGNMENT ============
    
    "mass_assignment": [
        "update_attributes", "update", "create", "save",
        "assign_attributes", "attributes=", "fill",
        "bind", "setProperties", "populate"
    ],
    
    # ============ OPEN REDIRECT ============
    
    "open_redirect": [
        "redirect", "Redirect", "redirect_to", "RedirectToAction",
        "sendRedirect", "setHeader(\"Location\"",
        "Location:", "url", "next", "return", "continue",
        "destination", "redirect_uri", "return_to"
    ],
    
    # ============ CLICKJACKING ============
    
    "clickjacking": [
        "X-Frame-Options", "frame-ancestors", "iframe",
        "frame", "frameset", "embed", "object"
    ],
    
    # ============ IDOR ============
    
    "idor": [
        "id=", "user_id", "userId", "account_id", "accountId",
        "order_id", "orderId", "document_id", "documentId",
        "file_id", "fileId", "object_id", "objectId"
    ],
    
    # ============ RATE LIMITING ============
    
    "rate_limiting": [
        "rate_limit", "ratelimit", "throttle", "Throttle",
        "RateLimiter", "TokenBucket", "LeakyBucket"
    ],
    
    # ============ WEBHOOKS ============
    
    "webhooks": [
        "webhook", "callback", "notify", "notification",
        "event", "trigger", "hook", "listener"
    ],
    
    # ============ GRAPHQL ============
    
    "graphql": [
        "graphql", "GraphQL", "query", "mutation", "subscription",
        "resolver", "schema", "type", "field", "argument",
        "introspection", "__schema", "__type"
    ],
    
    # ============ JWT ============
    
    "jwt": [
        "jwt", "JWT", "JsonWebToken", "jws", "JWS",
        "jwe", "JWE", "bearer", "Bearer", "token",
        "sign", "verify", "decode", "encode",
        "none", "HS256", "RS256", "ES256",

        # JWT attack extensions
        "alg:none", "\"alg\":\"none\"", "algorithm=None",
        "verify=False", "options={\"verify_signature\": False}",
        "jwks", "JWKS", "kid", "jku", "x5u",
        "PyJWT", "python-jose", "jsonwebtoken",
        "nimbus-jose-jwt", "System.IdentityModel.Tokens.Jwt",
        "RS256 to HS256", "key confusion"
    ],
    
    # ============ OAUTH ============
    
    "oauth": [
        "oauth", "OAuth", "oauth2", "OAuth2",
        "client_id", "client_secret", "authorization_code",
        "access_token", "refresh_token", "scope",
        "redirect_uri", "state", "nonce"
    ],
    
    # ============ SAML ============
    
    "saml": [
        "saml", "SAML", "SAMLResponse", "SAMLRequest",
        "Assertion", "AttributeStatement", "AuthnRequest",
        "SingleSignOn", "SSO", "IDP", "SP"
    ],
    
    # ============ EMAIL ============
    
    "email": [
        "mail", "email", "smtp", "SMTP", "send_mail",
        "sendmail", "PHPMailer", "SwiftMailer", "Nodemailer",
        "MailMessage", "SmtpClient", "MimeMessage",
        "to", "from", "cc", "bcc", "subject", "body",
        "attachment", "header injection"
    ],
    
    # ============ PDF ============
    
    "pdf": [
        "pdf", "PDF", "ReportLab", "PyPDF2", "pdfkit",
        "wkhtmltopdf", "PDFBox", "iText", "PdfSharp",
        "generatePdf", "createPdf", "renderPdf"
    ],
    
    # ============ IMAGE PROCESSING ============
    
    "image_processing": [
        "PIL", "Pillow", "ImageMagick", "GraphicsMagick",
        "GD", "gd", "image", "resize", "crop", "convert",
        "thumbnail", "watermark", "ImageSharp", "Sharp"
    ],
    
    # ============ ZIP/ARCHIVE ============
    
    "archive": [
        "zip", "unzip", "ZipFile", "zipfile", "tar",
        "tarfile", "gzip", "bz2", "rar", "7z",
        "compress", "decompress", "extract", "archive",
        "ZipArchive", "ZipInputStream", "TarArchive"
    ],
    
    # ============ TIME & DATE ============
    
    "time_date": [
        "time", "date", "datetime", "timestamp", "strtotime",
        "Date", "DateTime", "Calendar", "Instant",
        "LocalDateTime", "ZonedDateTime", "sleep", "usleep"
    ],
    
    # ============ UNICODE & ENCODING ============
    
    "encoding": [
        "encode", "decode", "unicode", "utf-8", "utf8",
        "ascii", "latin1", "iso-8859-1", "base64",
        "urlencode", "urldecode", "htmlentities",
        "html_entity_decode", "rawurlencode", "rawurldecode",
        "encodeURI", "decodeURI", "encodeURIComponent",
        "decodeURIComponent", "escape", "unescape"
    ],
    
    # ============ SERIALIZATION ============
    
    "serialization": [
        "serialize", "deserialize", "marshal", "unmarshal",
        "encode", "decode", "toJSON", "fromJSON",
        "stringify", "parse", "dump", "load"
    ],
    
    # ============ CACHE ============
    
    "cache": [
        "cache", "Cache", "memcache", "memcached", "redis",
        "Redis", "CacheManager", "IMemoryCache",
        "get", "set", "delete", "clear", "flush"
    ],
    
    # ============ QUEUE ============
    
    "queue": [
        "queue", "Queue", "celery", "rq", "bull",
        "RabbitMQ", "Kafka", "SQS", "PubSub",
        "enqueue", "dequeue", "publish", "subscribe"
    ],
    
    # ============ WEBSOCKET ============
    
    "websocket": [
        "websocket", "WebSocket", "ws", "wss",
        "socket.io", "SocketIO", "SignalR",
        "connect", "send", "receive", "broadcast"
    ],
    
    # ============ TESTING ============
    
    "testing": [
        "test", "Test", "unittest", "pytest", "jest",
        "mocha", "jasmine", "JUnit", "NUnit", "xUnit",
        "mock", "Mock", "stub", "spy", "fixture"
    ],
    
    # ============ CONFIGURATION ============
    
    "configuration": [
        "config", "configuration", "settings", "env",
        ".env", "config.json", "config.yaml", "config.xml",
        "appsettings.json", "web.config", "application.properties",
        "DEBUG", "PRODUCTION", "DEVELOPMENT", "SECRET_KEY"
    ]
}


ALL_KEYWORDS: List[str] = []
for cat, kws in CRITICAL_KEYWORDS_DICT.items():
    ALL_KEYWORDS.extend(kws)
ALL_KEYWORDS = list(set([kw.lower() for kw in ALL_KEYWORDS]))


# Curated keywords to add extra snippets for Tier 2/3 on large files (recall improvement).
RECALL_KEYWORDS: List[str] = [
    # NoSQL
    "$ne", "find_one", "update_one", "$set",
    # Session / JWT
    "session_id", "verify_exp", "jwt.decode(",
    "algorithms=", "algorithms=[",
    # JWT attacks
    "alg:\"none\"", "verify=false", "jwks_uri", "kid=",
    # Redirect
    "redirect(", "RedirectResponse", "redirect_url", "Redirect(",
    "next=", "return_to=", "redirect_uri=", "url=",
    # GraphQL
    "graphql", "__schema", "__type",
    # Archive / Zip Slip
    "extractall(", "extract(",
    "zipfile.zipfile(", "tarfile.open(",
    # Headers
    "x-forwarded-host", "x_forwarded_host", "X-Forwarded-Host",
    # Error / info disclosure
    "traceback", "format_exc",
    # Env / secrets
    "os.environ", "secret_key", "SECRET_KEY",
    "secret_key =", "api_key =", "password =", "private_key =",
    # Regex
    "re.compile", "re.match(", "re.search(",
    # HTTP requests
    "requests.get", "requests.post", "requests.put", "requests.delete",
    "urllib.request.urlopen", "httpx.get", "httpx.post",
    # SSRF metadata bypass
    "169.254.169.254", "metadata.google.internal", "computemetadata",
    # Deserialization
    "objectinputstream", "readobject(", "enabledefaulttyping", "@type",
    # Unsafe YAML / hash
    "yaml.load", "yaml.full_load", "hashlib.md5", "hashlib.sha1",
    # File ops
    "send_file", "send_from_directory", "os.path.join",
    "shutil.copy", "secure_filename",
    # Upload
    "introspection", "upload", "save(", "move_uploaded_file",
    "UploadFile", "file.filename", ".endswith(", "allowed_extensions", "content_type",
    # CSV
    "to_csv", "writerow", "csv.writer",
    # Request inputs
    "request.args", "request.form", "request.get_json", "request.values",
    # XSS
    "dangerouslySetInnerHTML", "innerHTML",
    # Redirect (client-side)
    "window.location.href", "location.href", "navigate(", "searchParams.get", "get(\'next\')",
    # Prototype pollution
    "__proto__", "Object.assign(", "constructor[prototype]", "_.merge(",
    "spread", "defaults, ...",
    # Token storage
    "localStorage.setItem", "setItem(\'token", "setItem(\"token",
    # HTTP smuggling
    "transfer-encoding", "content-length",
    # Race condition / TOCTOU
    "os.path.exists(", "time.sleep(", "asyncio.sleep(",
    # Mass assignment
    "**request.json", "**request.form", "**kwargs",
]
RECALL_KEYWORDS = list(set([k.lower() for k in RECALL_KEYWORDS]))


# ============ SEVERITY MAPPING ============

KEYWORD_SEVERITY: dict = {
    "command_injection":   "CRITICAL",
    "deserialization":     "CRITICAL",
    "code_injection":      "CRITICAL",
    "sql_injection":       "HIGH",
    "nosql_injection":     "HIGH",
    "xxe_injection":       "HIGH",
    "path_traversal":      "HIGH",
    "xss":                 "HIGH",
    "prototype_pollution": "HIGH",
    "http_smuggling":      "HIGH",
    "ldap_injection":      "HIGH",
    "template_injection":  "HIGH",
    "el_injection":        "HIGH",
    "network_ssrf":        "HIGH",
    "jwt":                 "HIGH",
    "authentication":      "MEDIUM",
    "authorization":       "MEDIUM",
    "cryptography":        "MEDIUM",
    "open_redirect":       "MEDIUM",
    "mass_assignment":     "MEDIUM",
    "idor":                "MEDIUM",
    "supply_chain":        "MEDIUM",
    "info_disclosure":     "MEDIUM",
    "file_operations":     "MEDIUM",
    "cookies_sessions":    "MEDIUM",
    "security_headers":    "LOW",
    "logging":             "LOW",
    "rate_limiting":       "LOW",
    "configuration":       "LOW",
    "testing":             "INFO",
}


# ============ CWE MAPPING ============

KEYWORD_CWE: dict = {
    "sql_injection":       "CWE-89",
    "nosql_injection":     "CWE-943",
    "command_injection":   "CWE-78",
    "code_injection":      "CWE-94",
    "xss":                 "CWE-79",
    "path_traversal":      "CWE-22",
    "deserialization":     "CWE-502",
    "xxe_injection":       "CWE-611",
    "network_ssrf":        "CWE-918",
    "open_redirect":       "CWE-601",
    "prototype_pollution": "CWE-1321",
    "http_smuggling":      "CWE-444",
    "cryptography":        "CWE-327",
    "jwt":                 "CWE-347",
    "ldap_injection":      "CWE-90",
    "xpath_injection":     "CWE-643",
    "template_injection":  "CWE-94",
    "el_injection":        "CWE-917",
    "idor":                "CWE-639",
    "mass_assignment":     "CWE-915",
    "authentication":      "CWE-287",
    "authorization":       "CWE-285",
    "info_disclosure":     "CWE-200",
    "file_operations":     "CWE-73",
    "concurrency":         "CWE-362",
    "memory_buffer":       "CWE-119",
    "security_headers":    "CWE-693",
    "cookies_sessions":    "CWE-614",
    "supply_chain":        "CWE-1104",
    "csv_injection":       "CWE-1236",
    "ssi_injection":       "CWE-97",
    "clickjacking":        "CWE-1021",
}

ALL_KEYWORDS: List[str] = []
for cat, kws in CRITICAL_KEYWORDS_DICT.items():
    ALL_KEYWORDS.extend(kws)
    
ALL_KEYWORDS = list(set([kw.lower() for kw in ALL_KEYWORDS]))

# Curated keywords to add extra snippets for Tier 2/3 on large files (recall improvement).
RECALL_KEYWORDS: List[str] = [
    "$ne", "find_one", "update_one", "$set", "session_id", "verify_exp", "jwt.decode",
    "redirect(", "RedirectResponse", "redirect_url", "Redirect(",
    "graphql", "__schema", "__type", "extractall", "extract(",
    "x-forwarded-host", "x_forwarded_host", "X-Forwarded-Host",
    "traceback", "format_exc", "os.environ", "secret_key", "SECRET_KEY",
    "re.compile", "re.match(", "re.search(", "requests.get", "requests.post", "requests.put", "requests.delete",
    "urllib.request.urlopen", "httpx.get", "httpx.post",
    "yaml.load", "yaml.full_load", "hashlib.md5", "hashlib.sha1",
    "send_file", "send_from_directory", "os.path.join", "shutil.copy", "secure_filename",
    "introspection", "upload", "save(", "move_uploaded_file", "to_csv", "writerow", "csv.writer",
    "request.args", "request.form", "request.get_json", "request.values",
    "algorithms=", "algorithms=[", "jwt.decode(",
    "UploadFile", "file.filename", ".endswith(", "allowed_extensions", "content_type",
    "window.location.href", "location.href", "navigate(", "searchParams.get", "get('next')",
    "__proto__", "Object.assign(", "spread", "defaults, ...",
    "localStorage.setItem", "setItem('token", "setItem(\"token",
    "dangerouslySetInnerHTML", "innerHTML",
]
RECALL_KEYWORDS = list(set([k.lower() for k in RECALL_KEYWORDS]))
