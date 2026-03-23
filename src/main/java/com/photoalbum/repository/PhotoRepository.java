package com.photoalbum.repository;

import com.photoalbum.model.Photo;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Repository interface for Photo entity operations
 */
@Repository
public interface PhotoRepository extends JpaRepository<Photo, String> {

    /**
     * Find all photos ordered by upload date (newest first)
     * @return List of photos ordered by upload date descending
     */
    // Migrated from Oracle to PostgreSQL according to Java check item 1: Convert all table and column names from uppercase to lowercase.
    // Migrated from Oracle to PostgreSQL according to Java check item 6: Use lowercase for identifiers in SQL string literals.
    @Query(value = "SELECT id, original_file_name, photo_data, stored_file_name, file_path, file_size, " +
                   "mime_type, uploaded_at, width, height " +
                   "FROM photos " +
                   "ORDER BY uploaded_at DESC",
           nativeQuery = true)
    List<Photo> findAllOrderByUploadedAtDesc();

    /**
     * Find photos uploaded before a specific photo (for navigation)
     * @param uploadedAt The upload timestamp to compare against
     * @return List of photos uploaded before the given timestamp, limited to 10
     */
    // Migrated from Oracle to PostgreSQL according to Java check item 17: Replace ROWNUM pagination with LIMIT/OFFSET.
    // Migrated from Oracle to PostgreSQL according to Java check item 6: Use lowercase for identifiers in SQL string literals.
    @Query(value = "SELECT id, original_file_name, photo_data, stored_file_name, file_path, file_size, " +
                   "mime_type, uploaded_at, width, height " +
                   "FROM photos " +
                   "WHERE uploaded_at < :uploadedAt " +
                   "ORDER BY uploaded_at DESC " +
                   "LIMIT 10",
           nativeQuery = true)
    List<Photo> findPhotosUploadedBefore(@Param("uploadedAt") LocalDateTime uploadedAt);

    /**
     * Find photos uploaded after a specific photo (for navigation)
     * @param uploadedAt The upload timestamp to compare against
     * @return List of photos uploaded after the given timestamp
     */
    // Migrated from Oracle to PostgreSQL according to Java check item 6: Use lowercase for identifiers in SQL string literals.
    // Migrated from Oracle to PostgreSQL according to Java check item 9999 (migrate all other Oracle-specific content): Replace Oracle NVL with PostgreSQL COALESCE.
    @Query(value = "SELECT id, original_file_name, photo_data, stored_file_name, " +
                   "COALESCE(file_path, 'default_path') AS file_path, file_size, " +
                   "mime_type, uploaded_at, width, height " +
                   "FROM photos " +
                   "WHERE uploaded_at > :uploadedAt " +
                   "ORDER BY uploaded_at ASC",
           nativeQuery = true)
    List<Photo> findPhotosUploadedAfter(@Param("uploadedAt") LocalDateTime uploadedAt);

    /**
     * Find photos by upload month using PostgreSQL EXTRACT function
     * @param year The year to search for
     * @param month The month to search for
     * @return List of photos uploaded in the specified month
     */
    // Migrated from Oracle to PostgreSQL according to Java check item 4: Replace TO_CHAR date functions with EXTRACT in SQL statements.
    // Migrated from Oracle to PostgreSQL according to Java check item 6: Use lowercase for identifiers in SQL string literals.
    @Query(value = "SELECT id, original_file_name, photo_data, stored_file_name, file_path, file_size, " +
                   "mime_type, uploaded_at, width, height " +
                   "FROM photos " +
                   "WHERE EXTRACT(YEAR FROM uploaded_at)::text = :year " +
                   "AND EXTRACT(MONTH FROM uploaded_at)::text = :month " +
                   "ORDER BY uploaded_at DESC",
           nativeQuery = true)
    List<Photo> findPhotosByUploadMonth(@Param("year") String year, @Param("month") String month);

    /**
     * Get paginated photos using PostgreSQL LIMIT/OFFSET.
     * @param startRow 0-based offset (number of rows to skip)
     * @param endRow Maximum number of rows to return (page size)
     * @return List of photos within the specified range
     */
    // Migrated from Oracle to PostgreSQL according to Java check item 17: Replace ROWNUM pagination with LIMIT/OFFSET.
    // Migrated from Oracle to PostgreSQL according to Java check item 6: Use lowercase for identifiers in SQL string literals.
    @Query(value = "SELECT id, original_file_name, photo_data, stored_file_name, file_path, file_size, " +
                   "mime_type, uploaded_at, width, height " +
                   "FROM photos ORDER BY uploaded_at DESC " +
                   "LIMIT :endRow OFFSET :startRow",
           nativeQuery = true)
    List<Photo> findPhotosWithPagination(@Param("startRow") int startRow, @Param("endRow") int endRow);

    /**
     * Find photos with file size statistics using PostgreSQL analytical functions
     * @return List of photos with rankings and running totals
     */
    // Migrated from Oracle to PostgreSQL according to Java check item 6: Use lowercase for identifiers in SQL string literals.
    // Migrated from Oracle to PostgreSQL according to Java check item 3: PostgreSQL supports RANK() OVER and SUM() OVER window functions natively.
    @Query(value = "SELECT id, original_file_name, photo_data, stored_file_name, file_path, file_size, " +
                   "mime_type, uploaded_at, width, height, " +
                   "RANK() OVER (ORDER BY file_size DESC) AS size_rank, " +
                   "SUM(file_size) OVER (ORDER BY uploaded_at ROWS UNBOUNDED PRECEDING) AS running_total " +
                   "FROM photos " +
                   "ORDER BY uploaded_at DESC",
           nativeQuery = true)
    List<Object[]> findPhotosWithStatistics();
}