-- group-by-year.lua
-- Pandoc Lua filter that groups bibliography entries by year with
-- reverse-chronological headings.
--
-- Requires: citeproc: false in YAML (so we control when citeproc runs).
-- If another filter (e.g. highlight-author) already ran citeproc,
-- this filter detects the existing refs div and skips the citeproc call.

--- Check whether the refs div already exists (citeproc already ran).
local function has_refs_div(blocks)
  local found = false
  blocks:walk({
    Div = function(div)
      if div.identifier == "refs" then
        found = true
      end
    end
  })
  return found
end

function Pandoc(doc)
  -- Build citation key -> year mapping from bibliography metadata
  local key_to_year = {}
  local refs = pandoc.utils.references(doc)
  for _, ref in ipairs(refs) do
    if ref.issued and ref.issued["date-parts"] then
      local dp = ref.issued["date-parts"]
      if dp[1] and dp[1][1] then
        key_to_year[ref.id] = tostring(dp[1][1])
      end
    end
  end

  -- Run citeproc only if it hasn't already been run by a previous filter
  if not has_refs_div(doc.blocks) then
    doc = pandoc.utils.citeproc(doc)
  end

  -- Find and restructure the #refs div
  doc.blocks = doc.blocks:walk({
    Div = function(div)
      if div.identifier ~= "refs" then
        return nil
      end

      -- Group by year
      local by_year = {}
      local year_order = {}
      for _, elem in ipairs(div.content) do
        if elem.t == "Div" then
          local key = elem.identifier:gsub("^ref%-", "")
          local year = key_to_year[key] or "Unknown"
          if not by_year[year] then
            by_year[year] = {}
            year_order[#year_order + 1] = year
          end
          by_year[year][#by_year[year] + 1] = elem
        end
      end

      -- Sort years descending (newest first)
      table.sort(year_order, function(a, b) return a > b end)

      -- Rebuild div content with year headings
      local new_content = pandoc.Blocks{}
      for _, year in ipairs(year_order) do
        new_content:insert(pandoc.Header(2, pandoc.Str(year), pandoc.Attr("section-" .. year)))
        for _, ref_div in ipairs(by_year[year]) do
          new_content:insert(ref_div)
        end
      end

      div.content = new_content
      return div
    end
  })

  return doc
end
