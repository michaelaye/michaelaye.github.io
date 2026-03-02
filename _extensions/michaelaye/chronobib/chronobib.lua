-- chronobib.lua
-- Pandoc/Quarto filter that groups bibliography entries by year with
-- reverse-chronological section headings.
--
-- Requires: citeproc: false in YAML (so this filter controls when citeproc runs).
-- If another filter (e.g. highlight-author) already ran citeproc,
-- this filter detects the existing refs div and skips the citeproc call.
--
-- Usage in YAML front matter:
--   citeproc: false
--   filters:
--     - michaelaye/chronobib
--
-- Optional configuration:
--   chronobib:
--     heading-level: 2    # heading level for year sections (default: 2)
--     sort: descending     # descending (default) or ascending

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
  -- Read configuration from metadata
  local heading_level = 2
  local sort_order = "descending"

  local meta = doc.meta["chronobib"]
  if meta then
    local meta_type = pandoc.utils.type(meta)
    if meta_type == "table" then
      if meta["heading-level"] then
        heading_level = tonumber(pandoc.utils.stringify(meta["heading-level"])) or 2
      end
      if meta["sort"] then
        sort_order = pandoc.utils.stringify(meta["sort"])
      end
    end
  end

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

  -- Find the refs div and replace it with year-grouped blocks
  local new_blocks = pandoc.Blocks{}
  for _, block in ipairs(doc.blocks) do
    if block.t == "Div" and block.identifier == "refs" then
      -- Extract ref attributes to preserve on per-year divs
      local ref_classes = block.classes
      local ref_attributes = block.attributes

      -- Group entries by year
      local by_year = {}
      local year_order = {}
      for _, elem in ipairs(block.content) do
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

      -- Sort years
      if sort_order == "ascending" then
        table.sort(year_order)
      else
        table.sort(year_order, function(a, b) return a > b end)
      end

      -- Emit year headings and ref divs as top-level blocks
      for _, year in ipairs(year_order) do
        new_blocks:insert(pandoc.Header(
          heading_level,
          pandoc.Str(year),
          pandoc.Attr("section-" .. year)
        ))
        -- Wrap each year's entries in a refs div to preserve bibliography styling
        local year_div = pandoc.Div(
          by_year[year],
          pandoc.Attr(
            "refs-" .. year,
            ref_classes,
            ref_attributes
          )
        )
        new_blocks:insert(year_div)
      end
    else
      new_blocks:insert(block)
    end
  end

  doc.blocks = new_blocks
  return doc
end
