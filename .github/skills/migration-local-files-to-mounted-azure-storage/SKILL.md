---
name: migration-local-files-to-mounted-azure-storage
description: Migrates Java applications from local file system paths to Azure-mounted storage paths using the AZURE_MOUNT_PATH environment variable. Updates file path references in Java code and Spring configuration. Use when migrating Java applications to Azure that read or write local files, or configuring Azure Storage mount points for containerized Java applications.
---

Your task is to migrate local files to mounted Azure Storage.

1. Update Java files

1.1. If the code is not reading or writing files, please do nothing.
1.2. If the local path string is in SPEL like this: @Value("${configured.directory:../sample}"), then just change local path string to ${AZURE_MOUNT_PATH:/mnt/azure} like this: @Value("${configured.directory:${AZURE_MOUNT_PATH:/mnt/azure}}")
1.3. If neither of the above two cases applies, then do the following:
    1.3.1. Define a "private static final" field pointing to the mount path, exactly as 'private static final String AZURE_MOUNT_PATH = System.getenv().getOrDefault("AZURE_MOUNT_PATH", "/mnt/azure");'
    1.3.2. Reference all original paths to the defined field.
1.4. Examples:
```diff
-@Value("${configured.directory:../sample}")
+@Value("${configured.directory:${AZURE_MOUNT_PATH:/mnt/azure}}")
```
```diff
-private static final String INPUT_DIR = "/Users/data/csv_inputs";
+private static final String AZURE_MOUNT_PATH = System.getenv().getOrDefault("AZURE_MOUNT_PATH", "/mnt/azure");
+private static final String INPUT_DIR = AZURE_MOUNT_PATH + "/data/csv_inputs";
```
```diff
-private static final String LOCAL_STATIC_LOCATION = "C:\\Users\\kiran\\Downloads\\imp downloads\\files\\static";
+private static final String AZURE_MOUNT_PATH = System.getenv().getOrDefault("AZURE_MOUNT_PATH", "/mnt/azure");
+private static final String LOCAL_STATIC_LOCATION = AZURE_MOUNT_PATH + "/files/static";
```
1.5. Requirements:
- DO modify: `File file = new File("C://some-folder/config.xml");`
- DO modify: `File file = new File("/Users/bob/config.xml");`
- DO modify: `File file = new File("/etc/config.xml");`
- DO modify: `Paths.get("C://some-folder/config.xml");`
- DO modify: `Path.of("C://some-folder/config.xml");`
- DO NOT modify: `File file = new File("/WEB-INF/config.xml");`
- DO NOT modify: `templateResolver.setPrefix("/WEB-INF/templates/");`
- DO NOT modify: `/src/main/resources`
- DO NOT modify: test files
- DO NOT modify: class name, method name, field name
- DO NOT modify: commented out code

## Update property files

1. Identify path
  1.1. Before making changes, carefully analyze each string to determine if it represents an actual file path:
    - Look for path patterns: Windows paths (C:\path\to\file), Unix paths (/home/user/file), or relative paths (./file or ../file)
    - Consider the context: In property files, not all strings with slashes are file paths
    - DO NOT modify URLs, database url, connection string, username, password, package names, or user identifiers that look like a local file path.
  1.2. Examples of non-local-file paths (IMPORTANT: DON'T CHANGE THEM):
    - spring.database.username="/home/test"
    - spring.database.url=jdbc:mysql://home/user/app:user@127.0.0.1:3306/database_name ("home/user/app" is not path, it's username in the database url.)
    - spring.datasource.schema=classpath:schema.sql
    - class: com.example.package/class
    - url: http://localhost:8080/api
2. Transform path
  2.1. Remove OS-specific prefix:
    - For Windows: Remove drive letter (e.g., C:)
    - For Unix: Remove root directories like /home, /usr, /Users
  2.2. Extract and preserve the application-specific portion of the path
  2.3. Add the Azure mount placeholder:
    - Standard format: "${AZURE_MOUNT_PATH}/your-path"
    - For Spring property files (application.yaml/yml/properties in src/main/resources), use "${AZURE_MOUNT_PATH:/mnt/azure}/your-path" to provide a default value
  2.4. Normalize all path delimiters to forward slashes (/)
3. Examples
  - Windows: "C:\Users\someone\logs\app.log" → "${AZURE_MOUNT_PATH}/logs/app.log"
  - Unix: "/etc/config.xml" → "${AZURE_MOUNT_PATH}/config.xml"
  - User directory: "/Users/bob/config.xml" → "${AZURE_MOUNT_PATH}/config.xml"
  - Relative: "./data/info.txt" → "${AZURE_MOUNT_PATH}/data/info.txt"
