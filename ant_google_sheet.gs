// This script is attached to the ANT google sheet template to help with data entry.
// 2025-11-07 release

function triggerAuthorization() {
  // A simple function to exercise library permissions
  const sheet = SpreadsheetApp.getActiveSpreadsheet();
  sheet.getActiveSheet(); // Example: Read the active sheet
}

function onEdit(e) {
  var lock = LockService.getDocumentLock();
  try {
    // Avoid re-entrancy (e.g., validations/formatting causing cascaded onEdits)
    lock.waitLock(5000);
  } catch (err) {
    // If we cannot acquire lock quickly, bail out
    return;
  }

  try {
    var ss = e.source;
    var editedSheet = ss.getActiveSheet();
    var editedRange = e.range;

    // DO NOT wrap text here; formatting changes can retrigger onEdit
    // e.range.setWrap(true);

// 1) ADDING ENTITIES 
   // Check if the edit is in the "Entities" tab and in the "Name" column (column A)
  if (editedSheet.getName() === "Entities" && e.range.rowStart > 1) {
    var newName = editedSheet.getRange(e.range.rowStart, 1).getValue().trim();
    
    if (newName !== '') {
      var existingSheet = ss.getSheetByName(newName);
      
      if (!existingSheet) {
        var currentSheet = ss.getActiveSheet();
        // Create a new sheet with the new entity name
        var currentCell = editedRange.getA1Notation()
        var newSheet = ss.insertSheet(newName);
        SpreadsheetApp.getUi().alert("New entity sheet called " + newSheet.getName() + " is being created.");
        ss.setActiveSheet(currentSheet);
        //var currentCell = editedRange.getA1Notation()
        editedSheet.getRange(currentCell).offset(0,1).activate(); //moves cursor to 2 cells to the right
        
        
        
        // Set the value of cell A1 to "Key" in bold
        newSheet.getRange("A1").setValue("Key").setFontWeight("bold");
        
        // Get the values from the edited row in the "Entities" sheet
        var entityRowValues = editedSheet.getRange(e.range.rowStart, 2, 1, editedSheet.getLastColumn()).getValues()[0];
        
        // Set the column headers and values in the new sheet
        for (var i = 0; i < entityRowValues.length; i++) {
          newSheet.getRange(1, i + 2).setValue(entityRowValues[i]).setFontWeight("bold");
        }
      } else {
        // Find the Color column from the edited sheet so we can ignore it
        // Get the header row (row 1) of the sheet
        var headerRow = editedSheet.getRange(1, 1, 1, editedSheet.getLastColumn()).getValues()[0];
        // Find the column index (0-based)
        var colorIndex = headerRow.findIndex(h => String(h).trim().toLowerCase() === "color");

        // Get the values from the edited row in the "Entities" sheet
        var entityRowValues = editedSheet.getRange(e.range.rowStart, 2, 1, editedSheet.getLastColumn()).getValues()[0];
        
        // Update column headers and values in the existing sheet
        var existingHeaders = existingSheet.getRange(1, 2, 1, existingSheet.getLastColumn()).getValues()[0];
        
        for (var i = 0; i < entityRowValues.length; i++) {
          if (i+1 == colorIndex) continue; // Skip Color column
          if (existingHeaders.indexOf(entityRowValues[i]) === -1) {
            var newColumn = existingSheet.getLastColumn() + 1;
            existingSheet.getRange(1, newColumn).setValue(entityRowValues[i]).setFontWeight("bold");
          }
        }
      }
    }
  }
    // 2) CREATING RELATIONSHIPS
    else if (editedSheet.getName() === "Relationships") {
      var row = e.range.getRow();
      var column = e.range.getColumn();

      // Only proceed when editing the Amount column (D = 4).
      // This prevents multiple runs while the row is still being filled out.
      if (row > 1 && column === 4) {
        var values = editedSheet.getRange(row, 1, 1, 4).getValues()[0];
        var entity1Name = String(values[0] || "").trim();
        var entity2SheetName = String(values[1] || "").trim();
        var relationName = String(values[2] || "").trim();
        var amountRaw = values[3];

        // Coerce amount to a safe non-negative integer
        var amountNum = Math.max(0, Math.floor(Number(amountRaw)));

        var entity1Sheet = ss.getSheetByName(entity1Name);
        if (entity1Sheet && relationName && amountNum > 0) {

          // Read full header row across max columns, then:
          // - Find the index of the last non-empty header (true last-used)
          // - Count exact matches of relationName
          var headersFull = entity1Sheet.getRange(1, 1, 1, entity1Sheet.getMaxColumns()).getValues()[0];

          var lastUsedIndex = -1; // 0-based index of last non-empty header cell
          var existingColumns = 0;
          for (var c = 0; c < headersFull.length; c++) {
            var h = String(headersFull[c] || "").trim();
            if (h !== "") lastUsedIndex = c;
            if (h === relationName) existingColumns++;
          }

          // Compute how many to add
          var num_add = amountNum - existingColumns;
          if (num_add <= 0) return; // nothing to add

          // Insert AFTER the last-used header cell
          // lastUsedIndex is 0-based column index; sheet columns are 1-based.
          // insertColumnsAfter(colNumber, howMany)
          var insertAfterCol = lastUsedIndex + 1; // convert to 1-based
          if (insertAfterCol < 1) insertAfterCol = 1; // safety

          entity1Sheet.insertColumnsAfter(insertAfterCol, num_add);

          // Clear formatting/validations on the newly inserted columns
          var newColsRange = entity1Sheet.getRange(
            1,
            insertAfterCol + 1,
            entity1Sheet.getMaxRows(),
            num_add
          );
          newColsRange.clear({ formatOnly: true });
          newColsRange.clearDataValidations();

          // Add headers for the new relation columns
          for (var k = 0; k < num_add; k++) {
            entity1Sheet
              .getRange(1, insertAfterCol + 1 + k)
              .setValue(relationName)
              .setFontWeight("bold");
          }

          // Apply validation from Entity2 list
          var entity2Sheet = ss.getSheetByName(entity2SheetName);
          if (entity2Sheet) {
            var entity2Range = entity2Sheet.getRange("A2:A");
            var rule = SpreadsheetApp.newDataValidation()
              .requireValueInRange(entity2Range)
              .setAllowInvalid(false)
              .build();

            entity1Sheet
              .getRange(
                2,
                insertAfterCol + 1,
                entity1Sheet.getMaxRows() - 1,
                num_add
              )
              .setDataValidation(rule)
              .setNumberFormat('@');
          }
        }
      }
    }

    // 3) CHECKING FOR DUPLICATE KEYS
    else if (editedRange.getColumn() == 1 && editedSheet.getRange(1, 1).getValue() == "Key") {
      var editedValue = e.value;
      var keyColumn = editedSheet.getRange(2, 1, editedSheet.getLastRow() - 1, 1);
      var keys = keyColumn.getValues();
      var count = 0;
      
      for (var i = 0; i < keys.length; i++) {
        if (keys[i][0] == editedValue) {
          count++;
          if (count == 2) {
            var errorMessage = "Duplicate key! Please enter a unique key.";
            var ui = SpreadsheetApp.getUi();
            var result = ui.alert('Error', errorMessage + '\n\nClick "OK" to fix the error before continuting.', ui.ButtonSet.OK);
            
            if (result == ui.Button.OK) {
              editedSheet.setActiveRange(keyColumn.getCell(i + 1, 1));
              keyColumn.getCell(i + 1, 1).setNote(errorMessage);
              keyColumn.getCell(i + 1, 1).setBackground("yellow");
            }
            return;
          }
        }
      }
      editedRange.setNote("");
      editedRange.setBackground("white");
    }

    // 4) CHECK BLANK KEYS
    if (editedSheet.getRange(1, editedRange.getColumn()).getValue() === "Key") {
      var editedValue2 = editedRange.getValue();
      var aboveValue = editedSheet.getRange(editedRange.getRow() - 1, editedRange.getColumn()).getValue();
      var aboveCell = editedSheet.getRange(editedRange.getRow() - 1, editedRange.getColumn());
      
      if (editedValue2 && !aboveValue) {
        aboveCell.setBackground("red");
        aboveCell.setNote("There cannot be empty keys");
        SpreadsheetApp.getUi().alert('Error: There cannot be empty keys. Please fix the issue.');
        SpreadsheetApp.setActiveSheet(editedSheet);
        SpreadsheetApp.getActiveRange().activate();
      }
    }
  } finally {
    // Always release the lock
    lock.releaseLock();
  }
}
