@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...), template_id: str = "saas"):
    try:
        logger.info(f"Processing {len(files)} files with template: {template_id}")
        # Parse files
        parsed_data = await FileParser.parse_files(files)
        
        # Generate insights
        insights = Insight_generator.generate_insights(parsed_data)
        
        # Generate slides
        slide_data = slid_generator_backend.generate_slides(parsed_data, insights, template_id)
        
        return JSONResponse(content=slide_data)
    except Exception as e:
        logger.error(f"Error processing files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")
