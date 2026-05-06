---
name: migration-log-to-console
description: Migrates Java application logging from file-based output to console-only output. Removes file appenders from logging configuration (logback, logging.xml) and ensures all log output goes to console. Use when containerizing Java applications, migrating to cloud-native logging, or preparing Java apps for Azure where console logging is preferred.
---

## Update the Java code to ensure logs are output only to the console

- If there is no log-related content in the Java file, then do nothing.
- If there is log-related content in the Java file, then make sure:
    - Logs are not output to files
    - Ensure logs are output to the console

## Update log configuration files to ensure logs are output only to the console

- If there is no log-related content in the configuration file, then do nothing.
- If there is log-related content in the configuration file, then make sure:
    - Keep using the original log configuration file (like logging.xml)
    - Ensure that logs are not output to files. All file appender references should be deleted.
    - Ensure that all logs are output to the console. All appender references should be console appender references.
- Your modifications should satisfy these requirements:
    - Modification should be as minimal as possible:
        - IMPORTANT: Don't delete file appender definition if deleting file appender references alone can ensure logs are not output to file. Example:
            ```properties
            rootLogger.appenderRefs=rolling # "rolling" is the file appender reference. Delete "rolling" reference, and use console appender reference instead.
            # The following 3 lines are file appender definition. Don't delete them to make fewer modifications.
            appender.rolling.type=RollingFile
            appender.rolling.name=RollingFileAppender
            appender.rolling.fileName=/logs/app.log
            ```
        - When deleting contents, remove them directly instead of converting them into comments.
        - Don't add or delete blank lines.
        - Don't add explanatory comments.
        - Don't introduce any unnecessary formatting changes (e.g., indentation adjustments).
    - If a log appender is included from another file, the reference should be updated accordingly. Example:
        ```diff
        -<include resource="org/springframework/boot/logging/logback/file-appender.xml"/>
        +<include resource="org/springframework/boot/logging/logback/console-appender.xml"/>
         <root level="${logging.level.root:-WARN}">
        -    <appender-ref ref="FILE" />
        +    <appender-ref ref="CONSOLE" />
         </root>
        ```
