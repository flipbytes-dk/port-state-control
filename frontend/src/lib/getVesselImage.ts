export async function getVesselImage(vesselName: string): Promise<string | null> {
  try {
    console.log('Fetching image for vessel:', vesselName);
    
    const apiKey = process.env.NEXT_PUBLIC_GOOGLE_API_KEY;
    const cx = process.env.NEXT_PUBLIC_GOOGLE_CX;
    
    if (!apiKey || !cx) {
      console.error('Missing API key or CX:', { apiKey, cx });
      return null;
    }

    const searchQuery = encodeURIComponent(`${vesselName} vessel ship marine traffic`);
    const url = `https://www.googleapis.com/customsearch/v1?key=${apiKey}&cx=${cx}&q=${searchQuery}&searchType=image&num=1&safe=active`;
    
    console.log('Request URL:', url);
    
    const response = await fetch(url);
    
    if (!response.ok) {
      console.error('Google API response not ok:', {
        status: response.status,
        statusText: response.statusText,
        url: response.url
      });
      const errorText = await response.text();
      console.error('Error response:', errorText);
      return null;
    }

    const data = await response.json();
    console.log('Google API response:', data);
    
    if (data.items && data.items.length > 0) {
      console.log('Found image URL:', data.items[0].link);
      return data.items[0].link;
    }
    
    console.log('No images found in response');
    return null;
  } catch (error) {
    console.error('Error fetching vessel image:', error);
    return null;
  }
} 