# b-tree

### Vortrag ca. 40 minuten
https://www.youtube.com/watch?v=aZjYr87r1b8


- Alle Leafs müssen auf gleicher Höhe sein.
- Degree(in der Literatur oft als 'd', 't', 'k' oder 'm' bezeichnet) ist in der praxis entweder die maximale Anzahl der Leafs, in diesem Fall ist die maximale Anzahl von Keys d - 1, oder die minimale Anzahl der Leafs, in disem Fall ist die Anzahl der Keys 2d - 1.

Suchanfrage für DBeaver Sample Database (Zeit in DBeaver steht rechts unten!)
```sql
-- Track 3500 Rows InvoiceLine 2240
SELECT
    Ar.Name AS ArtistName,
    G.Name AS GenreName,
    COUNT(DISTINCT T.TrackId) AS NumberOfUniqueTracksSold,
    SUM(IL.Quantity) AS TotalUnitsSold,
    SUM(IL.UnitPrice * IL.Quantity) AS TotalSalesAmount,
    AVG(IL.UnitPrice) AS AverageUnitPrice,
    MAX(I.InvoiceDate) AS LatestSaleDate
FROM
    InvoiceLine AS IL
JOIN
    Track AS T ON IL.TrackId = T.TrackId
JOIN
    Album AS Al ON T.AlbumId = Al.AlbumId
JOIN
    Artist AS Ar ON Al.ArtistId = Ar.ArtistId
JOIN
    Genre AS G ON T.GenreId = G.GenreId
JOIN
    Invoice AS I ON IL.InvoiceId = I.InvoiceId
JOIN
    Customer AS C ON I.CustomerId = C.CustomerId
GROUP BY
    Ar.Name,
    G.Name
ORDER BY
    TotalSalesAmount DESC,
    ArtistName ASC;	
```