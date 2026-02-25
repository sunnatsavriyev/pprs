import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useComing_Application_DetailQuery,
  useDeletePhotoMutation,
  useMEQuery,
} from "@/services/api";
import { VisuallyHidden } from "@radix-ui/react-visually-hidden";
import { Download, DownloadCloud } from "lucide-react";

import { Input } from "@/components/ui/input";
import {
  IconCalendarWeek,
  IconFileTypography,
  IconMessage,
  IconSection,
  IconUserQuestion,
} from "@tabler/icons-react";
import { useState } from "react";
import Coming_Application_Details_Work_Pogress from "./coming-application-work-prosess";
const statusVariantMap = {
  "bajarilgan": "success",
  "qaytarildi": "destructive",
  "qabul qilindi": "default",
  "jarayonda": "warning",
};

export default function Application_details_Main({ id }) {
  const { data, isLoading } = useComing_Application_DetailQuery(id);
  const [DeletePhotos, { isLoading: DeleteLoadingPhoto }] =
    useDeletePhotoMutation();
  const { data: me } = useMEQuery();
  const [selectedImages, setSelectedImages] = useState([]);
  const [showImageModal, setShowImageModal] = useState(false);
  const [currentImage, setCurrentImage] = useState(null);
  const [currentImageId, setCurrentImageId] = useState(null);
  const [showFileModal, setShowFileModal] = useState(false);

  if (isLoading || !data) {
    return (
      <ScrollArea className="h-[calc(100vh-110px)] no-scrollbar pr-4">
        <div className="space-y-3 p-3">
          <Skeleton className="h-6 w-[150px] rounded mb-3" />
          <Skeleton className="h-40 w-full rounded-md" />
          <Skeleton className="h-4 w-full rounded" />
          <Skeleton className="h-4 w-[80%] rounded" />
          <Skeleton className="h-4 w-[60%] rounded" />
        </div>
      </ScrollArea>
    );
  }

  const toggleSelectImage = (img) => {
    setSelectedImages((prev) =>
      prev.includes(img) ? prev.filter((i) => i !== img) : [...prev, img],
    );
  };

  const downloadImage = async (url, filename) => {
    const response = await fetch(url);
    const blob = await response.blob();

    const blobUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = blobUrl;
    link.download = filename;

    document.body.appendChild(link);
    link.click();

    link.remove();
    window.URL.revokeObjectURL(blobUrl);
  };

  const downloadImages = async () => {
    try {
      for (let i = 0; i < selectedImages.length; i++) {
        await downloadImage(selectedImages[i], `rasm-${i + 1}.jpg`);
      }
    } catch (error) {
      console.error("Images download error:", error);
    }
  };

  const handleDownloadFile = async (url, filename = "file") => {
    try {
      const res = await fetch(url);
      const blob = await res.blob();

      const blobUrl = URL.createObjectURL(blob);
      const link = document.createElement("a");

      link.href = blobUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();

      link.remove();
      URL.revokeObjectURL(blobUrl);
    } catch (error) {
      console.error("File download error:", error);
    }
  };

  return (
    <ScrollArea className="no-scrollbar h-screen pb-35">
      <div className="space-y-4 ">
        <Card className="w-full outline-none p-4 pb-3">
          <CardContent className="p-0 border-none space-y-6">
            {/* Top: Ariza va Actions Dropdown */}
            <div className="flex items-center justify-between gap-4">
              {/* Ariza info */}
              <div className="flex-1">
                <p className="text-lg font-semibold  mb-2">
                  Ariza raqami: #{data?.id}
                </p>
                <Badge
                  variant={statusVariantMap[data?.status] || "outline"}
                  className="text-xs"
                >
                  {data?.status}
                </Badge>
              </div>
              {/* Actions Dropdown */}
              <Button onClick={() => setShowFileModal(true)}>
                Bildirgi fayli <DownloadCloud className="ml-1" size={17} />
              </Button>
            </div>

            {/* Umumiy ma'lumot */}
            <div className="space-y-4 border-t pt-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Sana */}
                <div className="flex items-start gap-3">
                  <IconCalendarWeek
                    stroke={2}
                    className="h-4 w-4 text-blue-600 mt-1 flex-shrink-0"
                  />
                  <div>
                    <p className="text-xs text-muted-foreground">
                      Ariza sanasi
                    </p>
                    <p className="text-sm font-medium">
                      {data?.sana || "Mavjud emas"}
                    </p>
                  </div>
                </div>

                {/* Turi */}
                <div className="flex items-start gap-3">
                  <IconFileTypography
                    stroke={2}
                    className="h-4 w-4 text-blue-600 mt-1 flex-shrink-0"
                  />
                  <div>
                    <p className="text-xs text-muted-foreground">Turi</p>
                    <p className="text-sm font-medium">
                      {data?.turi || "—"}{" "}
                      {data?.ijro_muddati ? `(${data?.ijro_muddati})` : ""}
                    </p>
                  </div>
                </div>

                {/* Yaratuvchi */}
                <div className="flex items-start gap-3">
                  {data?.kim_tomonidan?.photo ? (
                    <Dialog className="text-white">
                      {/* ✅ TRIGGER — faqat bitta element */}
                      <DialogTrigger className="text-white" asChild>
                        <img
                          src={data.kim_tomonidan.photo}
                          alt="Yaratuvchi rasmi"
                          className="w-6 h-6 rounded-full cursor-pointer hover:opacity-80 transition text-white"
                        />
                      </DialogTrigger>

                      <DialogContent className="max-w-md p-2">
                        {/* ✅ ACCESSIBILITY UCHUN */}
                        <VisuallyHidden>
                          <DialogTitle>Yaratuvchi rasmi</DialogTitle>
                        </VisuallyHidden>

                        <img
                          src={data.kim_tomonidan.photo}
                          alt="Yaratuvchi rasmi"
                          className="w-full h-auto rounded-lg text-white"
                        />
                      </DialogContent>
                    </Dialog>
                  ) : (
                    <IconUserQuestion
                      stroke={2}
                      className="h-4 w-4 text-blue-600 mt-1 flex-shrink-0"
                    />
                  )}

                  <div>
                    <p className="text-xs text-muted-foreground">Yaratuvchi</p>
                    <p className="text-sm font-medium">
                      {data?.created_by || "—"}
                    </p>
                  </div>
                </div>

                {/* Tuzilmalar */}
                <div className="flex items-start gap-3">
                  <IconSection
                    stroke={2}
                    className="h-4 w-4 text-blue-600 mt-1 flex-shrink-0"
                  />
                  <div>
                    <p className="text-xs text-muted-foreground">
                      Ariza beruvchi tuzilma
                    </p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      <Badge>{data?.kim_tomonidan?.name}</Badge>
                    </div>
                  </div>
                </div>
              </div>

              {/* Comment section */}
              {data?.comment && (
                <div className="flex gap-3">
                  <IconMessage
                    stroke={2}
                    className="h-4 w-4 text-orange-600 mt-1 flex-shrink-0"
                  />
                  <div className="flex-1">
                    <p className="text-xs text-muted-foreground mb-1">Izoh</p>
                    <p className="text-sm text-gray-600 dark:text-gray-300 ">
                      {data.comment}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
        {/* Rasmlar */}
        <Card className="w-full p-4 ">
          <CardContent className="p-0">
            <p className="font-medium text-sm mb-2">Rasmlar</p>
            {data?.rasmlar?.length ? (
              <>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
                  {data.rasmlar.map((r) => (
                    <div key={r.id} className="relative group">
                      <img
                        src={r.rasm || "/placeholder.svg"}
                        alt="ariza rasm"
                        className="w-full h-24 object-cover rounded cursor-pointer  hover:opacity-80 transition-opacity"
                        onClick={() => {
                          setCurrentImage(r.rasm);
                          setCurrentImageId(r.id);
                          setShowImageModal(true);
                        }}
                      />
                      <Input
                        type="checkbox"
                        className="absolute w-4 h-4 rounded-full top-1 right-1 cursor-pointer"
                        checked={selectedImages.includes(r.rasm)}
                        onChange={() => toggleSelectImage(r.rasm)}
                        aria-label="Select image"
                      />
                    </div>
                  ))}
                </div>
                {selectedImages.length > 0 && (
                  <Button onClick={downloadImages} className="w-full mt-5">
                    <Download className="h-4 w-4 mr-2 " />
                    Tanlanganlarni yuklab olish ({selectedImages.length})
                  </Button>
                )}
              </>
            ) : (
              <p className="text-xs text-muted-foreground">Rasm topilmadi</p>
            )}
          </CardContent>
        </Card>
        <Coming_Application_Details_Work_Pogress data={data} />
        {/* Image Modal */}
        <Dialog open={showImageModal} onOpenChange={setShowImageModal}>
          <DialogContent className="sm:max-w-lg w-full">
            <DialogHeader>
              <DialogTitle>Rasmni ko'rish</DialogTitle>
              <DialogClose />
            </DialogHeader>
            {currentImage && (
              <>
                <img
                  src={currentImage || "/placeholder.svg"}
                  alt="modal rasm"
                  className="w-full h-auto rounded"
                />
                <div>
                  <Button
                    variant="link"
                    onClick={() =>
                      handleDownloadFile(currentImage, "image.jpg")
                    }
                    className="w-full"
                  >
                    <Download className="h-4 w-4 mr-2" />
                  </Button>
                </div>
              </>
            )}
          </DialogContent>
        </Dialog>
        {/* File Modal */}
        <Dialog open={showFileModal} onOpenChange={setShowFileModal}>
          <DialogContent className="sm:max-w-md w-full">
            <DialogHeader>
              <DialogTitle>Yuklab olish</DialogTitle>
              <DialogClose />
            </DialogHeader>
            <p className="text-xs text-muted-foreground mb-2">
              {data?.comment}
            </p>
            {data?.bildirgi && (
              <Button
                onClick={() => handleDownloadFile(data.bildirgi, "file")}
                className="w-full"
              >
                <Download className="h-4 w-4 mr-2" />
                Yuklab olish
              </Button>
            )}
          </DialogContent>
        </Dialog>
      </div>
    </ScrollArea>
  );
}
