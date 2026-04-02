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
     * Migrated from Oracle to PostgreSQL according to Java check item 1: Convert all table and column names to lowercase.
     * Migrated from Oracle to PostgreSQL according to Java check item 6: Use lowercase for identifiers, uppercase for SQL keywords.
     * @return List of photos ordered by upload date descending
     */
    @Query(value = "SELECT id, original_file_name, photo_data, stored_file_name, file_path, file_size, " +
                   "mime_type, uploaded_at, width, height " +
                   "FROM photos " +
                   "ORDER BY uploaded_at DESC",
           nativeQuery = true)
    List<Photo> findAllOrderByUploadedAtDesc();

    /**
     * Find photos uploaded before a specific photo (for navigation)
     * Migrated from Oracle to PostgreSQL according to Java check item 17: Replace ROWNUM pagination with LIMIT/OFFSET.
     * Migrated from Oracle to PostgreSQL according to Java check item 1: Convert all table and column names to lowercase.
     * @param uploadedAt The upload timestamp to compare against
     * @return List of photos uploaded before the given timestamp
     */
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
     * Migrated from Oracle to PostgreSQL according to Java check item 1: Convert all table and column names to lowercase.
     * Migrated from Oracle to PostgreSQL according to ORM check item 4: Replace NVL function with COALESCE.
     * @param uploadedAt The upload timestamp to compare against
     * @return List of photos uploaded after the given timestamp
     */
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
     * Migrated from Oracle to PostgreSQL according to Java check item 4: Replace TO_CHAR date functions with EXTRACT.
     * Migrated from Oracle to PostgreSQL according to Java check item 1: Convert all table and column names to lowercase.
     * @param year The year to search for
     * @param month The month to search for
     * @return List of photos uploaded in the specified month
     */
    @Query(value = "SELECT id, original_file_name, photo_data, stored_file_name, file_path, file_size, " +
                   "mime_type, uploaded_at, width, height " +
                   "FROM photos " +
                   "WHERE EXTRACT(YEAR FROM uploaded_at)::text = :year " +
                   "AND EXTRACT(MONTH FROM uploaded_at)::text = :month " +
                   "ORDER BY uploaded_at DESC",
           nativeQuery = true)
    List<Photo> findPhotosByUploadMonth(@Param("year") String year, @Param("month") String month);

    /**
     * Get paginated photos using PostgreSQL ROW_NUMBER window function
     * Migrated from Oracle to PostgreSQL according to Java check item 17: Replace ROWNUM pagination with LIMIT/OFFSET.
     * Migrated from Oracle to PostgreSQL according to Java check item 3: Replace Oracle-specific SQL functions with PostgreSQL equivalents.
     * @param startRow Starting row number (1-based, inclusive)
     * @param endRow Ending row number (inclusive)
     * @return List of photos within the specified row range
     */
    @Query(value = "SELECT id, original_file_name, photo_data, stored_file_name, file_path, file_size, " +
                   "mime_type, uploaded_at, width, height " +
                   "FROM (" +
                   "SELECT *, ROW_NUMBER() OVER (ORDER BY uploaded_at DESC) AS rn " +
                   "FROM photos" +
                   ") ranked " +
                   "WHERE rn >= :startRow AND rn <= :endRow",
           nativeQuery = true)
    List<Photo> findPhotosWithPagination(@Param("startRow") int startRow, @Param("endRow") int endRow);

    /**
     * Find photos with file size statistics using PostgreSQL analytical functions
     * Migrated from Oracle to PostgreSQL according to Java check item 1: Convert all table and column names to lowercase.
     * Migrated from Oracle to PostgreSQL according to Java check item 6: Use lowercase for identifiers, uppercase for SQL keywords.
     * Note: RANK() and SUM() window functions work natively in PostgreSQL.
     * @return List of photos with running totals and rankings
     */
    @Query(value = "SELECT id, original_file_name, photo_data, stored_file_name, file_path, file_size, " +
                   "mime_type, uploaded_at, width, height, " +
                   "RANK() OVER (ORDER BY file_size DESC) AS size_rank, " +
                   "SUM(file_size) OVER (ORDER BY uploaded_at ROWS UNBOUNDED PRECEDING) AS running_total " +
                   "FROM photos " +
                   "ORDER BY uploaded_at DESC",
           nativeQuery = true)
    List<Object[]> findPhotosWithStatistics();
}