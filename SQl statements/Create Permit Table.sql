CREATE TABLE Permit (SYNumber INT,
					 NumberPlate VarChar(8),
					 FOREIGN KEY (SYNumber) REFERENCES Users (SYNumber),
					 FOREIGN KEY (NumberPlate) REFERENCES Car (NumberPlate),
					 PRIMARY KEY (SYNumber, NumberPlate),
					 HasPermit BIT,
					 ValidFrom DATE,
					 ValidUntil DATE
);