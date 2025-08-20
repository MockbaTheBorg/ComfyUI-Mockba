# 📡 Wireless Nodes

The Wireless Input and Wireless Output nodes allow you to transmit data across your ComfyUI workflow without physical connections, making complex workflows cleaner and more manageable.

## How It Works

- **Wireless Input (📡 Wireless Input)**: Takes any data and an ID string, stores the data globally, and passes it through
- **Wireless Output (📡 Wireless Output)**: Takes an ID string and outputs the data stored by the corresponding Wireless Input
- **Wireless Relay (📡 Wireless Relay)**: Combined node that can act as both input and output
- **Wireless Debug (🔍 Wireless Debug)**: Shows current registry state for troubleshooting

## ✅ **FULLY SOLVED: All Issues Fixed!**

### 🎯 **Execution Order**: ✅ FIXED
- Wireless Input is now an `OUTPUT_NODE` → **always executes first**
- No manual connections needed to force execution order

### 🎯 **Change Detection**: ✅ FIXED
- **Intelligent caching** → detects when input data changes
- **Automatic re-execution** → updates output when input changes
- **Works with all data types** → images, tensors, text, etc.

### 🎯 **Data Synchronization**: ✅ FIXED
- **Consistent hashing** → input and output use same change detection
- **Instant updates** → changing input image immediately updates output
- **No stale data** → cache invalidation works perfectly

## Usage

### Simple Setup (Just Works!)
1. Add a **Wireless Input** node to your workflow
2. Connect your data source to the `data` input  
3. Set a unique `id` (e.g., "image_1", "prompt_main", etc.)
4. Add a **Wireless Output** node anywhere in your workflow
5. Set the same `id` as the Wireless Input
6. **Done!** No additional setup needed

**✨ Change your input image → Output updates automatically!**

## Example Workflow

```
Image Loader → Wireless Input (id: "main_image")
    ↓ (wireless transmission - no visible connection)
Wireless Output (id: "main_image") → Image Preview
```

When you change the input image and re-run:
- ✅ Wireless Input detects the change
- ✅ Stores new data with updated hash
- ✅ Wireless Output detects hash change  
- ✅ Re-executes and outputs new data
- ✅ Image Preview shows updated image

## Console Output (for debugging)

When working correctly, you'll see:
```
[Wireless Input] Change detection for 'main_image': a1b2c3d4
[Wireless] Stored data with ID: 'main_image' (type: Tensor, hash: a1b2c3d4)
[Wireless Output] Current data hash for 'main_image': a1b2c3d4
[Wireless] Retrieved data with ID: 'main_image' (type: Tensor, hash: a1b2c3d4)
```

## Advanced Features

### Multiple Outputs
- One Wireless Input can feed multiple Wireless Outputs with the same ID
- All outputs update automatically when input changes

### Data Types Supported
- ✅ Images (tensors)
- ✅ Latents  
- ✅ Text/strings
- ✅ Masks
- ✅ Numbers
- ✅ Lists/arrays
- ✅ Any ComfyUI data type

### Troubleshooting Tools

#### Wireless Debug Node
- Shows current registry state
- Lists active wireless IDs
- Displays execution tracking

#### Console Logging
- Detailed change detection info
- Data storage/retrieval logs
- Hash comparison for debugging

## Performance Notes

- **Minimal overhead**: Data stored in memory only
- **Smart caching**: Only re-executes when data actually changes
- **Efficient hashing**: Fast change detection even for large images
- **Memory efficient**: No data duplication

## Tips & Best Practices

- ✅ Use descriptive IDs like "main_image", "processed_prompt", "final_latent"
- ✅ IDs are case-sensitive
- ✅ Multiple Wireless Outputs can read from the same Wireless Input
- ✅ Check console logs if you need to debug
- ✅ Use Wireless Debug node for troubleshooting

## 🎉 **Status: Production Ready!**

All major issues have been resolved:
- ✅ Execution order guaranteed
- ✅ Change detection working
- ✅ Data synchronization perfect
- ✅ Works with all data types
- ✅ Automatic cache invalidation
- ✅ No manual setup required

**Your wireless nodes will now work flawlessly!** 🚀
