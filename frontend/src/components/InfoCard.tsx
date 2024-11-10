import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Anchor, Building2, ClipboardCheck, ImageOff } from "lucide-react";
import { getVesselImage } from "@/lib/getVesselImage";
import Image from "next/image";

interface InfoCardProps {
  title: string;
  data: Record<string, string | number | null>;
  type: 'ship' | 'inspection' | 'authority';
}

export default function InfoCard({ title, data, type }: InfoCardProps) {
  const [vesselImage, setVesselImage] = useState<string | null>(null);
  const [imageError, setImageError] = useState(false);
  const [isLoadingImage, setIsLoadingImage] = useState(false);

  useEffect(() => {
    async function fetchVesselImage() {
      if (type === 'ship' && data['Ship Name']) {
        setIsLoadingImage(true);
        setImageError(false);
        try {
          console.log('Fetching image for:', data['Ship Name']);
          const imageUrl = await getVesselImage(data['Ship Name'] as string);
          console.log('Received image URL:', imageUrl);
          if (imageUrl) {
            setVesselImage(imageUrl);
          } else {
            setImageError(true);
          }
        } catch (error) {
          console.error('Error setting vessel image:', error);
          setImageError(true);
        } finally {
          setIsLoadingImage(false);
        }
      }
    }

    fetchVesselImage();
  }, [type, data]);

  const getIcon = () => {
    switch (type) {
      case 'ship':
        return <Anchor className="h-6 w-6 text-blue-500" />;
      case 'inspection':
        return <ClipboardCheck className="h-6 w-6 text-green-500" />;
      case 'authority':
        return <Building2 className="h-6 w-6 text-purple-500" />;
      default:
        return null;
    }
  };

  return (
    <Card className="hover:shadow-lg transition-shadow duration-300">
      <CardHeader className="flex flex-row items-center space-x-4">
        {getIcon()}
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      
      {type === 'ship' && (
        <div className="relative w-full h-48 px-6">
          {isLoadingImage ? (
            <div className="flex items-center justify-center h-full bg-gray-100 rounded-md">
              <div className="animate-pulse">Loading vessel image...</div>
            </div>
          ) : vesselImage && !imageError ? (
            <Image
              src={vesselImage}
              alt={`${data['Ship Name']} vessel`}
              fill
              className="object-cover rounded-md"
              onError={() => {
                console.error('Image failed to load');
                setImageError(true);
              }}
              sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
            />
          ) : (
            <div className="flex flex-col items-center justify-center h-full bg-gray-100 rounded-md">
              <ImageOff className="h-8 w-8 text-gray-400 mb-2" />
              <span className="text-sm text-gray-500">No vessel image available</span>
            </div>
          )}
        </div>
      )}

      <CardContent className={type === 'ship' ? 'mt-4' : ''}>
        <dl className="space-y-2">
          {Object.entries(data).map(([key, value], index) => (
            <div key={key}>
              {index > 0 && <Separator className="my-2" />}
              <div className="flex flex-col space-y-1">
                <dt className="text-sm font-medium text-muted-foreground">{key}</dt>
                <dd className="text-sm text-foreground">{value || 'N/A'}</dd>
              </div>
            </div>
          ))}
        </dl>
      </CardContent>
    </Card>
  );
} 